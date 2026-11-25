"""Ejecuta I-02 con el Python actual, sin registrar kernels ni cambiar configuración."""

import sys
import os
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    carpeta_ipython = ROOT / 'tmp/ipython-I02'
    carpeta_ipython.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('IPYTHONDIR', str(carpeta_ipython))
    path = ROOT / 'notebooks/01_exploracion_encovi.ipynb'
    notebook = nbformat.read(path, as_version=4)
    manager = KernelManager(kernel_name='python3')
    manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    client = NotebookClient(notebook, km=manager, timeout=300,
                            resources={'metadata': {'path': str(ROOT)}})
    try:
        client.execute()
        nbformat.write(notebook, path)
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    print('I-02: notebook ejecutado y resultados agregados guardados.')


if __name__ == '__main__':
    main()
