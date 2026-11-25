"""Publicación de CSV, JSON y manifiesto por generación indivisible."""
import csv
from decimal import Decimal
from hashlib import sha256
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

FIELDS = (
    "id", "regla", "anio", "territorios", "grupo", "motivo", "magnitudes",
    "evidencias", "explicacion", "pregunta", "evidencia_requerida",
    "limitacion", "robustez",
)


def _number(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Tipo no serializable: {type(value).__name__}")


def json_text(item, indent=None):
    return json.dumps(item, ensure_ascii=False, allow_nan=False, indent=indent,
                      default=_number, separators=(",", ":") if indent is None else None)


def _csv_cell(value):
    if isinstance(value, (list, dict)):
        return json_text(value)
    return "" if value is None else str(value)


def serialize(result, raw_hashes):
    json_bytes = (json_text(result, indent=2) + "\n").encode("utf-8")
    public = json.loads(json_bytes)
    records = public["hallazgos"]
    ids = [f["id"] for f in records]
    if len(ids) != len(set(ids)) or sum(public["conteos"].values()) != len(ids):
        raise ValueError("IDs repetidos o conteos incompatibles")
    csv_output = io.StringIO(newline="")
    writer = csv.DictWriter(csv_output, FIELDS, lineterminator="\n")
    writer.writeheader()
    expected = []
    for row in records:
        if set(row) != set(FIELDS):
            raise ValueError("Campos de ficha incompatibles")
        cells = {key: _csv_cell(row[key]) for key in FIELDS}
        writer.writerow(cells)
        expected.append(cells)
    csv_output.seek(0)
    reader = csv.DictReader(csv_output)
    if tuple(reader.fieldnames or ()) != FIELDS or list(reader) != expected:
        raise ValueError("Las fichas CSV y JSON difieren")
    manifest = {"algoritmo": "sha256", "archivos_brutos": raw_hashes}
    return {
        "hallazgos.json": json_bytes,
        "hallazgos.csv": csv_output.getvalue().encode("utf-8"),
        "radar_fuentes.json": (json_text(manifest, indent=2) + "\n").encode("utf-8"),
    }


def publish(output_dir, payloads):
    """El único punto de activación es el reemplazo atómico de 'actual'."""
    store = output_dir / ".radar_m04"
    store.mkdir(parents=True, exist_ok=True)
    digest = sha256()
    for name, data in sorted(payloads.items()):
        digest.update(name.encode() + b"\0" + sha256(data).digest())
    version = digest.hexdigest()
    generation = store / version
    with TemporaryDirectory(dir=store, prefix="preparando-") as temporary:
        stage = Path(temporary)
        new = stage / "archivos"
        new.mkdir()
        for name, data in payloads.items():
            (new / name).write_bytes(data)
        try:
            new.rename(generation)
        except OSError:
            # Otro escritor puede haber instalado exactamente esta generación.
            if not generation.is_dir() or any(
                (generation / name).read_bytes() != data for name, data in payloads.items()
            ):
                raise
        for name in payloads:
            alias = output_dir / name
            target = Path(".radar_m04", "actual", name)
            try:
                alias.symlink_to(target)
            except FileExistsError:
                if not alias.is_symlink() or alias.readlink() != target:
                    raise ValueError(f"Destino ajeno al radar: {name}") from None
        pointer = stage / "actual"
        pointer.symlink_to(version, target_is_directory=True)
        os.replace(pointer, store / "actual")
