FROM frolvlad/alpine-glibc:alpine-3.6

ENV CONDA_DIR="/opt/conda"
ENV PATH="$CONDA_DIR/bin:$PATH"

# Base layer to build from with Anaconda
RUN CONDA_VERSION="4.3.30" && \
    CONDA_MD5_CHECKSUM="0b80a152332a4ce5250f3c09589c7a81" && \
    \
    apk add --no-cache --virtual=.build-dependencies-base wget ca-certificates bash && \
    \
    mkdir -p "$CONDA_DIR" && \
    wget "http://repo.continuum.io/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh" -O miniconda.sh && \
    echo "$CONDA_MD5_CHECKSUM  miniconda.sh" | md5sum -c && \
    bash miniconda.sh -f -b -p "$CONDA_DIR" && \
    echo "export PATH=$CONDA_DIR/bin:\$PATH" > /etc/profile.d/conda.sh && \
    rm miniconda.sh && \
    \
    conda update --all --yes && \
    conda config --set auto_update_conda False && \
    # cleanup
     rm -r "$CONDA_DIR/pkgs/" && \
    \
    # delete apk cache stuff
    apk del .build-dependencies-base && \
    mkdir -p "$CONDA_DIR/locks" && \
    chmod 777 "$CONDA_DIR/locks"

# gcc & math (skipping MKL libraries to save space)
RUN apk add --no-cache --virtual=.build-dependencies-gcc gcc g++ musl-dev redis && \
    pip install --no-cache \
                       implicit \
                       numpy \
                       nmslib \
                       redis \
                       sanic \
                       scipy \
                       pandas && \
    conda clean --all && \
    rm -r "$CONDA_DIR/pkgs/" && \
    find /opt/conda/lib/python3.*/ -name 'tests' -exec rm -r '{}' +
    # TODO: reinstate later when gcc stuff figured out
    # && \ apk del .build-dependencies-gcc