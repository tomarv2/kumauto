# FROM golang:1.10

# WORKDIR /
# # ADD ./test_dockerfile1 /test/test_dockerfile1
# # ADD ./test_dockerfile2 /test/test_dockerfile2

# RUN go get github.com/prometheus/alertmanager/cmd/amtool
# # RUN amtool check-config  /test/test_dockerfile1

# RUN go get github.com/prometheus/prometheus/cmd/promtool
# # RUN promtool check config /test/test_dockerfile2

FROM python:3.6
RUN apt-get update
RUN apt-get install -y vim \
    net-tools

ADD . ./automation/

RUN git config --global user.email demo@demo.com
RUN git config --global user.name demo

RUN pip install -r ./automation/requirements.txt


# gcc for cgo
RUN apt-get update && apt-get install -y --no-install-recommends \
		g++ \
		gcc \
		libc6-dev \
		make \
		pkg-config \
	&& rm -rf /var/lib/apt/lists/*

RUN wget https://dl.google.com/go/go1.13.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.13.linux-amd64.tar.gz
RUN rm go1.13.linux-amd64.tar.gz

RUN export PATH="/usr/local/go/bin:$PATH" \
	go version

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

RUN go get github.com/prometheus/alertmanager/cmd/amtool

RUN go get github.com/prometheus/prometheus/cmd/promtool