# For prior setup, follow steps here - https://learn.hashicorp.com/terraform/gcp/intro
provider "google" {
    project = "${var.project_id}"
    region  = "${var.region}"
    zone    = "${var.zone}"
}

terraform {
    backend "gcs" {
        bucket  = "terraform-254112"
        prefix  = "terraform/state/"
    }
}

# Terraform State Bucket - Required to be in root file
# Initially created in GCP Console, then imported:
#   terraform import google_storage_bucket.terraform-254112 PROJECT_ID/terraform-254112
resource "google_storage_bucket" "terraform-254112" {
    name          = "terraform-254112"
    location      = "${var.region}"
    project       = "${var.project_id}"
    storage_class = "STANDARD"
}

resource "google_storage_bucket_acl" "terraform-254112-acl" {
    bucket            = "${google_storage_bucket.terraform-254112.name}"
    predefined_acl    = "private"
}

# Terraform Service Account
# Initially created in GCP Console, then imported:
#   terraform import google_service_account.terraform projects/PROJECT_ID/serviceAccounts/terraform@PROJECT_ID.iam.gserviceaccount.com
resource "google_service_account" "terraform" {
  account_id   = "terraform"
  display_name = "terraform"
}