resource "google_project_iam_binding" "kubernetes-developer" {
    project = "${var.project_id}"
    role    = "roles/container.developer"

    members = [
        "user:${var.kubernetes-developer-user-email}",
    ]
}

resource "google_service_account" "cloud-sql-user" {
  account_id   = "cloud-sql-user"
  display_name = "cloud-sql-user"
}

resource "google_project_iam_binding" "cloud-sql-client" {
    project = "${var.project_id}"
    role    = "roles/cloudsql.client"

    members = [
        "serviceAccount:${google_service_account.cloud-sql-user.email}"
    ]
}