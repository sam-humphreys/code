variable "project" {
    type          = "string"
    description   = "Project name"
}

variable "project_id" {
    type          = "string"
    description   = "Project ID"
}

variable "region" {
    type          = "string"
    description   = "Project region"
}

variable "zone" {
    type          = "string"
    description   = "Project zone"
}

variable "kubernetes-developer-group-email" {
    type          = "string"
    description   = "Email address for a Google group, to grant a Kubernetes developer role"
}