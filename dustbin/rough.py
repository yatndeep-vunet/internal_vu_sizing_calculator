data = [
    ["Sizing on a Managed K8S Environment (Openshift, AKS, EKS, GKE etc)"],
    [
        "Worker Group",
        "vCPUs",
        "Memory",
        "Num Workers",
        "Storage(GB)",
        "Warm Storage (GB)",
        "Cold Storage (GB)",
        "AWS EC2 Plan",
    ],
    ["Core and Support Services", 8, 16, 2, 500, 0, 0, "c6g.2xlarge8"],
    ["Storage and Pipelines", 12, 24, 3, "", "", "", "m6g.4xlarge"],
    ["Ingress and Data Hub", 16, 24, 4, "", "", "", "c6g.4xlarge16"],
    ["vuSiteManager", 8, 16, 1, "", "", "", "c6g.2xlarge8"],
    ["TOTAL", 124, 216, 10, 500],
    [],
    [],
]

header = data[1][0:7]
rows = [row[:-1] if i < 4 else row for i, row in enumerate(data[2:7])]

print(rows)
