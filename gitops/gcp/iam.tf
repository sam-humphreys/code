resource "google_project_iam_binding" "kubernetes-developer" {
    project = "${var.project_id}"
    role    = "roles/container.developer"

    members = [
        "group:${var.kubernetes-developer-group-email}",
    ]
}