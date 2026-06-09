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
  tags = [
    "${REGISTRY}-huggingfaceserver:${TAG}-gpu",
    "${REGISTRY}-huggingfaceserver:latest-gpu",
  ]
  cache-to = ["type=inline"]
}
