resource "google_compute_network" "vpc-network" {
    project                 = "${var.project_id}"
    name                    = "vpc-network"
    auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vpc-subnetwork" {
    name            = "vpc-subnetwork"
    project         = "${var.project_id}"
    region          = "${var.region}"
    ip_cidr_range   = "10.2.0.0/16"
    network         = "${google_compute_network.vpc-network.name}"

    secondary_ip_range {
        range_name      = "${var.project_id}-vpc-subnetwork-services"
        ip_cidr_range   = "10.4.0.0/20"
    }

    secondary_ip_range {
        range_name      = "${var.project_id}-vpc-subnetwork-pods"
        ip_cidr_range   = "10.8.0.0/16"
    }
}

# Static IP address for exposing UI deployment (referenced in UI Ingress)
resource "google_compute_address" "ui-static-ip" {
    project = "${var.project_id}"
    region  = "${var.region}"
    name    = "ui-static-ip"
}