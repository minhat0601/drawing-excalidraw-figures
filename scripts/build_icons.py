#!/usr/bin/env python3
"""Rebuild assets/icons.json from .excalidrawlib libraries (MIT sources only).

    python3 scripts/build_icons.py <path-to-excalidraw-libraries/libraries>

Source: https://github.com/excalidraw/excalidraw-libraries (MIT). Each icon keeps only
its geometry fields; colors are ignored because ve.py recolors by token when drawing.
A source with a name list keeps only those items (the AWS library has 249; the skill needs
the common services only). AWS icons are AWS trademarks: AWS allows them in architecture
diagrams, so keep the service name as the label under the icon.
"""
import json, pathlib, re, sys

AWS = ('EC2', 'Lambda', 'ECS', 'EKS', 'Fargate', 'ECR', 'Auto Scaling group', 'S3', 'EBS', 'EFS', 'Glacier',
       'RDS', 'Aurora', 'DynamoDB', 'ElastiCache', 'MemoryDB for Redis', 'Redshift', 'OpenSearch Service',
       'SQS', 'SNS', 'EventBridge', 'Kinesis Data Streams', 'Managed Streaming for Apache Kafka', 'Step Functions',
       'CloudFront', 'Route 53', 'ELB', 'ALB', 'NLB', 'API Gateway', 'VPC', 'NAT gateway', 'Internet gateway',
       'IAM', 'Cognito', 'KMS', 'Secrets Manager', 'WAF', 'CloudWatch')
AZURE_A = ('Virtual Machine', 'App Service', 'SQL Database', 'Blob Storage', 'Data Lake', 'Virtual Network',
           'Network Security Group', 'Key Vault', 'Active Directory', 'Service Bus Namespace', 'Application Insights',
           'Azure DevOps')
AZURE_B = ('Azure Cosmos DB', 'Azure Cache for Redis', 'Azure Event Hubs', 'Azure Database for Postgres',
           'Azure Database for MySQL', 'Azure Databricks', 'Azure Synapse Analytics')
GCP = ('Compute Engine', 'GKE', 'Cloud Run', 'Cloud Function', 'App Engine', 'Cloud Storage', 'Cloud SQL', 'Cloud Spanner',
       'Cloud Bigtable', 'Cloud Firestore', 'Cloud Memorystore', 'Bigquery', 'Pub Sub', 'Dataflow', 'Dataproc',
       'Cloud Load Balancing', 'Cloud CDN', 'Cloud DNS', 'Cloud NAT', 'Virtual Private Cloud', 'Cloud Armor', 'Cloud IAM',
       'Cloud KMS', 'Secret Manager', 'Cloud Logging', 'Cloud Monitoring', 'Cloud Build', 'Artifact Registry', 'Vertex AI')
DB_MWC = ('Postgres Database', 'MySQL Database', 'Snowflake')
DB_CHUQ = ('Cassandra', 'Elasticsearch', 'Kafka')
# technology-logos is an old-format library (no names): pick items by index and name them here
TECH_LOGOS = {0: 'Kubernetes', 5: 'Terraform', 16: 'Neo4j', 17: 'Redis'}
TEN_NGAN = {'Cloud Function': 'Cloud Functions', 'Postgres Database': 'postgres', 'MySQL Database': 'mysql', 'Managed Streaming for Apache Kafka': 'msk', 'MemoryDB for Redis': 'memorydb',
            'OpenSearch Service': 'opensearch', 'Kinesis Data Streams': 'kinesis'}
NGUON = [  # (path inside libraries/, name prefix[, names to keep])
    ('mateuszbaransanok/it-icons.excalidrawlib', ''),
    ('dwelle/network-topology-icons.excalidrawlib', 'net-'),
    ('dhtoran/stick-people.excalidrawlib', ''),
    ('finfin/flow-chart-symbols.excalidrawlib', 'flow-'),
    ('anna-pastushko/architecture-diagram-components.excalidrawlib', 'arch-'),
    ('childishgirl/aws-architecture-icons.excalidrawlib', 'aws-', AWS),
    ('youritjang/azure-cloud-services.excalidrawlib', 'azure-', AZURE_A),
    ('rockssk/microsoft-azure-cloud-icons.excalidrawlib', 'azure-', AZURE_B),
    ('mguidoti/google-icons.excalidrawlib', 'gcp-', GCP),
    ('mwc360/microsoft-fabric-architecture-icons.excalidrawlib', 'db-', DB_MWC),
    ('chuqbach/data-platform.excalidrawlib', 'db-', DB_CHUQ),
    ('maeddes/technology-logos.excalidrawlib', 'tech-', TECH_LOGOS),
]
def rutgon(pre, ten):
    """Short key name: explicit TEN_NGAN override, else drop the redundant 'Azure ' prefix under azure-."""
    return TEN_NGAN.get(ten) or (re.sub(r'^Azure ', '', ten) if pre == 'azure-' else ten)


GIU = ('type', 'x', 'y', 'width', 'height', 'angle', 'points', 'strokeColor', 'backgroundColor', 'fillStyle',
       'strokeWidth', 'strokeStyle', 'roundness', 'startArrowhead', 'endArrowhead')
goc = pathlib.Path(sys.argv[1])
out = {}
for rel, pre, *chon in NGUON:
    d = json.loads((goc / rel).read_text(encoding='utf-8'))
    items = d.get('libraryItems') or [{'elements': x, 'name': ''} for x in d.get('library', [])]
    for i, it in enumerate(items):
        ten = (it.get('name') or '').strip() or (chon[0].get(i, '') if chon and isinstance(chon[0], dict) else '')
        ten0, ten = ten, rutgon(pre, ten)
        # opacity 0 = invisible hit area the library author put around the icon: drop it, or it renders as a circle
        els = [e for e in it.get('elements', []) if not e.get('isDeleted') and e.get('opacity', 100) > 0
               and e.get('type') in ('rectangle', 'ellipse', 'diamond', 'line', 'arrow')]
        if not ten or not els or (chon and not isinstance(chon[0], dict) and ten0 not in chon[0]):
            continue
        key = pre + re.sub(r'[^a-z0-9]+', '-', ten.lower()).strip('-')
        gon = []
        for e in els:
            o = {k: e[k] for k in GIU if k in e}
            if 'roundness' not in o and e.get('strokeSharpness') == 'round':
                o['roundness'] = {'type': 2 if e['type'] in ('line', 'arrow') else 3}
            for k in ('x', 'y', 'width', 'height'):
                o[k] = round(o.get(k, 0), 2)
            if 'points' in o:
                o['points'] = [[round(p[0], 2), round(p[1], 2)] for p in o['points']]
            gon.append(o)
        out[key] = {'elements': gon, 'src': rel.split('/')[0]}
for rel, pre, *chon in NGUON:
    thieu = [t for t in ((chon[0].values() if isinstance(chon[0], dict) else chon[0]) if chon else ()) if pre + re.sub(r'[^a-z0-9]+', '-', rutgon(pre, t).lower()).strip('-') not in out]
    if thieu:
        sys.exit(f'{rel}: names not found {thieu}')
dst = pathlib.Path(__file__).resolve().parents[1] / 'assets' / 'icons.json'
dst.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(len(out), 'icons ->', dst, f'{dst.stat().st_size // 1024}KB')
