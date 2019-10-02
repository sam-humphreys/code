resource "google_container_cluster" "cluster" {
    name        = "cluster"
    project     = "${var.project_id}"
    location    = "${var.zone}"

    remove_default_node_pool    = true
    initial_node_count          = 1

    network     = "${google_compute_network.vpc-network.name}"
    subnetwork  = "${google_compute_subnetwork.vpc-subnetwork.name}"

    maintenance_policy {
        daily_maintenance_window {
            start_time = "03:00"
        }
    }
}

resource "google_container_node_pool" "preemptible-pool" {
    name        = "preemptible-pool"
    location    = "${var.zone}"
    project     = "${var.project_id}"
    cluster     = "${google_container_cluster.cluster.name}"

    initial_node_count = 1

    autoscaling {
        min_node_count = 1
        max_node_count = 5
    }

    node_config {
        preemptible     = true
        disk_size_gb    = 60
        machine_type    = "n1-standard-2"

        metadata = {
            disable-legacy-endpoints = "true"
        }

        oauth_scopes = [
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
            "https://www.googleapis.com/auth/compute",
            "https://www.googleapis.com/auth/devstorage.read_write",
        ]
    }
}