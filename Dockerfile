FROM jupyter/datascience-notebook

ADD requirements.txt .

RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

# install extension - table of contents
RUN jupyter nbextension install --user https://rawgithub.com/minrk/ipython_extensions/master/nbextensions/toc.js
RUN curl -L https://rawgithub.com/minrk/ipython_extensions/master/nbextensions/toc.css > $(jupyter --data-dir)/nbextensions/toc.css
RUN jupyter nbextension enable toc

WORKDIR /code
ADD . .
