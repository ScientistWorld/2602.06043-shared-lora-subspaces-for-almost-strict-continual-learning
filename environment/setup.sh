#!/bin/bash
# Install Python packages into the container overlay.
#
# This script is run by the system on the login node (which has internet)
# inside the container with a persistent overlay. Changes persist across
# job submissions without rebuilding the container.
#
# Put ALL pip installs here, NOT in container.def.
# Only use container.def for the base Docker image and apt-get packages.
#
# IMPORTANT: Install into the SYSTEM Python, not a virtual environment.
# The overlay may be recreated on container rebuilds — a venv inside
# it will be lost and all subsequent jobs will fail.
# Use: uv pip install --system <packages>
# Do NOT create a venv (python -m venv, virtualenv, etc.).

set -e

# Versions used by the completed reproduction and hardening jobs. Both are
# public PyPI releases; no local model weights or external datasets are needed.
uv pip install --system numpy==2.4.6 torch==2.12.0
