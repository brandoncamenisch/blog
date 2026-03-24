FROM python:3.12-slim

ARG COMFYUI_REF=v0.3.38

RUN apt-get update \
  && apt-get install -y --no-install-recommends git libgl1 libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone https://github.com/comfyanonymous/ComfyUI.git \
  && cd ComfyUI \
  && git checkout "$COMFYUI_REF" \
  && pip install --no-cache-dir -r requirements.txt

WORKDIR /opt/ComfyUI

EXPOSE 8188

CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188", "--output-directory", "/workspace/output", "--input-directory", "/workspace/input", "--user-directory", "/workspace/user", "--extra-model-paths-config", "/workspace/extra_model_paths.yaml"]
