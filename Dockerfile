# start by pulling the python image
FROM python:3.11-alpine

# switch working directory
WORKDIR /app

# install Node
RUN apk add --no-cache nodejs npm

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt
COPY ./package.json /app/package.json

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# build CSS
RUN npm install
RUN npm run build:css

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["main.py" ]