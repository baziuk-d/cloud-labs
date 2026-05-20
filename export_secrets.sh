#!/bin/bash
export PROJECT_ID=$(gcloud config get-value project)
export GCP_PROJECT_ID=${PROJECT_ID}
export GCP_REGION="europe-west1"

export DB_USER=$(gcloud secrets versions access latest --secret="DB_USER" --project=${PROJECT_ID})
export DB_HOST=$(gcloud secrets versions access latest --secret="DB_HOST" --project=${PROJECT_ID})
export DB_NAME=$(gcloud secrets versions access latest --secret="DB_NAME" --project=${PROJECT_ID})
export DB_PASSWORD=$(gcloud secrets versions access latest --secret="DB_PASSWORD" --project=${PROJECT_ID})
export DB_PORT=$(gcloud secrets versions access latest --secret="DB_PORT" --project=${PROJECT_ID})
export IDENTITY_KEY=$(gcloud secrets versions access latest --secret="IDENTITY_KEY" --project=${PROJECT_ID})

