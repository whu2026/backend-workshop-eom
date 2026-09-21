"""Maak eigen YAML-bestanden; wijzigt niets in Kubernetes."""
import argparse
import json
from pathlib import Path
import re
import shlex

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("naam", help="Vooraf toegewezen unieke naam, bijvoorbeeld a01")
    p.add_argument("--config", default="config/workshop.json")
    p.add_argument("--oplossing", action="store_true", help="Vul ook images en hosts in")
    p.add_argument("--output", help="Optionele nieuwe uitvoermap")
    args = p.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,18}[a-z0-9]|[a-z]", args.naam):
        p.error("Gebruik 1–20 kleine letters/cijfers/koppeltekens; begin met letter.")
    root = Path(__file__).resolve().parents[1]
    cp = Path(args.config)
    if not cp.is_absolute():
        cp = root / cp
    cfg = json.loads(cp.read_text())
    for k in ("ingress_class", "base_domain", "image_repository", "web_image"):
        value = cfg.get(k)
        if not isinstance(value, str) or not value or "VUL_" in value or any(c.isspace() for c in value):
            p.error(f"Begeleider moet {k} invullen in {cp}")
    out = Path(args.output).resolve() if args.output else root / "werk" / args.naam
    if out.exists():
        p.error(f"{out} bestaat al; bestaande bestanden blijven behouden.")
    web, sim = "nginx-demo-deployment-" + args.naam, "sim-" + args.naam
    web_app = "nginx-demo-" + args.naam
    web_service = "nginx-demo-service-" + args.naam
    web_ingress = "nginx-demo-ingress-" + args.naam
    web_configmap = "nginx-demo-html-" + args.naam
    image = cfg["image_repository"] + ":" + args.naam + "-new-v1"
    secret = cfg.get("image_pull_secret", "")
    tls = cfg.get("tls_secret", "")
    for value in (secret, tls):
        if value and not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", value):
            p.error("Ongeldige Secret-naam")
    replacements = {"__NAAM__": args.naam, "__WEB_DEPLOYMENT__": web, "__WEB_APP__": web_app, "__WEB_SERVICE__": web_service, "__WEB_INGRESS__": web_ingress, "__WEB_CONFIGMAP__": web_configmap, "__SIM__": sim,
        "__CLASS__": cfg["ingress_class"],
        "__PULL_SECRET__": "      imagePullSecrets:\n        - name: " + secret if secret else "",
        "__TLS__": "  tls:\n    - hosts:\n        - VUL_HOST_IN\n      secretName: " + tls if tls else ""}
    hosts = {"stap-1": "nginx-web-" + args.naam + "." + cfg["base_domain"], "stap-2": sim + "." + cfg["base_domain"]}
    out.mkdir(parents=True)
    for step in hosts:
        folder = "nginx" if step == "stap-1" else step
        (out/folder).mkdir()
        for f in (root/step/"templates").glob("*.yaml"):
            text = f.read_text()
            for a, b in replacements.items(): text = text.replace(a, b)
            if args.oplossing:
                text = text.replace("VUL_HOST_IN", hosts[step]).replace("VUL_IMAGE_IN", cfg["web_image"] if step == "stap-1" else image)
            (out/folder/f.name).write_text(text)
    env = {"NAAM": args.naam, "NS": "backend-workshop", "WEB": web, "WEB_APP": web_app, "WEB_SERVICE": web_service, "WEB_INGRESS": web_ingress, "WEB_CONFIGMAP": web_configmap, "SIM": sim,
        "IMAGE": image, "WEB_IMAGE": cfg["web_image"], "WEB_HOST": hosts["stap-1"],
        "SIM_HOST": hosts["stap-2"], "SCHEME": "https" if tls else "http", "WORK": str(out)}
    (out/"workshop.env").write_text("\n".join("export " + k + "=" + shlex.quote(v) for k,v in env.items()) + "\n")
    print("Gemaakt:", out)
    print("Voer in Bash uit: source", shlex.quote(str(out/"workshop.env")))

if __name__ == "__main__": main()
