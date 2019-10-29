resource "google_sql_database_instance" "master" {
    name                = "master"
    region              = "${var.region}"
    project             = "${var.project_id}"
    database_version    = "POSTGRES_9_6"

    settings {
        tier = "db-f1-micro"

        maintenance_window {
            # Sunday's @ 6pm
            day     = 7
            hour    = 18
        }

        backup_configuration {
            enabled = true
        }
    }
}

resource "google_sql_database" "monitoring" {
    name        = "monitoring"
    instance    = "${google_sql_database_instance.master.name}"
    project     = "${var.project_id}"
}

resource "google_sql_user" "monitoring-user" {
    name        = "monitoring-rw"
    instance    = "${google_sql_database_instance.master.name}"
    password    = "monitoringrules"
}