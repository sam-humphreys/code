resource "google_storage_bucket" "store-data" {
  name          = "${var.project_id}-store-data"
  location      = "${var.region}"
  project       = "${var.project_id}"
  storage_class = "REGIONAL"
}
