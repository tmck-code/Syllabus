FROM jupyter/datascience-notebook

ADD requirements.txt .

USER root
RUN apt update && \
    apt install -y --no-install-recommends nodejs time fortune fortunes
USER jovyan

# RUN bash -c "$(wget -q -O - https://linux.kite.com/dls/linux/current)"

RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

# install extensions
# - table of contents
RUN jupyter labextension install \
    @jupyterlab/toc
    # @krassowski/jupyterlab_go_to_definition
    # @lckr/jupyterlab_variableinspector

WORKDIR /code
ADD . .
