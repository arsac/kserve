group "default" {
  targets = ["huggingfaceserver-gpu"]
}

variable "REGISTRY" {
  default = "git.mlxa.dev/arsac/kserve"
}

variable "TAG" {
  default = "latest"
}

variable "SOURCE" {
  default = ""
}

target "_base" {
  labels = merge(
    SOURCE != "" ? {
      "org.opencontainers.image.source" = SOURCE
    } : {},
    {}
  )
}

target "huggingfaceserver-gpu" {
  inherits   = ["_base"]
  context    = "python"
  dockerfile = "huggingface_server.Dockerfile"
  platforms  = ["linux/amd64"]
  # latest-gpu intentionally NOT published here: the dated ${TAG}-gpu image is
  # built first and promoted to latest-gpu only after GPU validation passes, so
  # an unvalidated build never becomes the prod base.
  tags = [
    "${REGISTRY}-huggingfaceserver:${TAG}-gpu",
  ]
  cache-to = ["type=inline"]
}
