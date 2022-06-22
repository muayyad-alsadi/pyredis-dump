ARG PYTHON_VERSION=alpine

FROM python:$PYTHON_VERSION as base

ENV APP_ROOT=/app
WORKDIR $APP_ROOT
 
RUN python -m venv $APP_ROOT/venv
ENV PATH="$APP_ROOT/venv/bin:$PATH"

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

FROM base as compile

ENV USER_ID=65535
ENV GROUP_ID=65535
ENV USER_NAME=python
ENV GROUP_NAME=python

RUN addgroup -g $USER_ID $GROUP_NAME && \
    adduser --shell /bin/nologin --disabled-password \
    --no-create-home --uid $USER_ID --ingroup $GROUP_NAME $USER_NAME && \
    chown $USER_NAME:$GROUP_NAME $APP_ROOT

WORKDIR $APP_ROOT

COPY --chown=$USER_NAME:$GROUP_NAME --from=base $APP_ROOT/venv ./venv
COPY --chown=$USER_NAME:$GROUP_NAME . .

USER $USER_NAME

ENV PATH="$APP_ROOT/venv/bin:$PATH"
