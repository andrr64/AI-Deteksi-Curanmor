conda install -c conda-forge libstdcxx-ng
pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu118
conda install -c nvidia cuda-toolkit=11.8
pip install -r requirements.txt