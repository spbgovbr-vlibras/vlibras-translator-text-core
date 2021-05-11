#FROM anibali/pytorch:1.6.0-cuda10.2
FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN apt-get update && apt-get install -y build-essential curl openjdk-8-jdk make

RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash

RUN apt-get install -y git-lfs

RUN apt-get install -y libhunspell-dev -y && pip install Cython

RUN git lfs install

#RUN apt-get install -y dirmngr && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EA8CACC073C3DB2A

#RUN echo "deb http://ppa.launchpad.net/linuxuprising/java/ubuntu bionic main" | sudo tee /etc/apt/sources.list.d/linuxuprising-java.list && apt-get update

#RUN apt-get install -y oracle-java11-installer oracle-java11-set-default

ADD worker translator-text-worker/

WORKDIR translator-text-worker/

RUN git clone https://github.com/pytorch/fairseq

RUN cd fairseq ; pip install --editable ./

#RUN pip install --no-cache-dir -Iv --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-translate==1.2.0

RUN pip install --no-cache-dir --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-translate==1.2.2rc1

RUN pip install --no-cache-dir --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-deeplearning==1.2.1rc1

#RUN pip install vlibras-deeplearning

RUN make install

RUN pip show fairseq ; pip show vlibras-translate

CMD make start 
