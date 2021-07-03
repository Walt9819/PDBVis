# base image
FROM walt22/stuff:pdbvis
# setup environment variable
ENV DockerHOME=/home/app/webapp

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip

# port where the Django app runs
EXPOSE 8000

# Get app from repo
RUN git clone https://github.com/Walt9819/PDBVis.git

# Get into app
#RUN cd $DockerHOME/PDBVis

# Create models directory
RUN mkdir -p $DockerHOME/PDBVis/models
RUN mkdir -p $DockerHOME/PDBVis/models/pdb
RUN mkdir -p $DockerHOME/PDBVis/models/fbx

# run this command to install all dependencies
RUN pip3 install -r $DockerHOME/PDBVis/requirements.txt

# Copy files from main code
#COPY . $DockerHOME

# set into app directory
RUN cd $DockerHOME/PDBVis

# make migrations
RUN python3 manage.py migrate

# start server
CMD ["python3", "manage.py", "runserver"]
# CMD ["python3", "$DockerHOME/PDBVis/manage.py", "runserver"] local testing

# Build image
# PS D:\Documentos\DRX\PDBVis_API\Website\PDBVis> docker build -t pdbvistest . --no-cache
# Run image
# docker run --rm -it -p 8080:8000 --name pdbvis101  pdbvistest bash
