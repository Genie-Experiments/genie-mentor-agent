from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    CfnOutput,
    Duration,
    RemovalPolicy,
)
from constructs import Construct


class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        self.vpc = ec2.Vpc(self, "VPC", max_azs=2, nat_gateways=1)

        # Create Security Group for RDS
        self.db_security_group = ec2.SecurityGroup(
            self,
            "DatabaseSecurityGroup",
            vpc=self.vpc,
            description="Security group for Genie Mentor Agent database",
            allow_all_outbound=True,
        )

        # Allow inbound traffic on PostgreSQL port
        self.db_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow PostgreSQL traffic"
        )

        # Create Parameter Group for pgvector extension
        parameter_group = rds.ParameterGroup(
            self,
            "ParameterGroup",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13_7
            ),
            parameters={
                "shared_preload_libraries": "pg_stat_statements,pgvector",
                "pg_stat_statements.track": "all",
            },
            description="Parameter group for PostgreSQL with pgvector extension",
        )

        # Create RDS Instance
        self.db_instance = rds.DatabaseInstance(
            self,
            "Database",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13_7
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MEDIUM
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.db_security_group],
            allocated_storage=20,
            storage_type=rds.StorageType.GP2,
            database_name="genie_mentor_bot",
            credentials=rds.Credentials.from_generated_secret("postgres"),
            parameter_group=parameter_group,
            backup_retention=Duration.days(7),
            deletion_protection=False,
            removal_policy=RemovalPolicy.SNAPSHOT,
            multi_az=True,
            publicly_accessible=False,
            auto_minor_version_upgrade=True,
        )

        # Outputs
        CfnOutput(
            self,
            "DatabaseEndpoint",
            value=self.db_instance.db_instance_endpoint_address,
            description="Database endpoint",
        )

        CfnOutput(
            self, "DatabaseName", value="genie_mentor_bot", description="Database name"
        )

        CfnOutput(
            self,
            "DatabaseSecretArn",
            value=self.db_instance.secret.secret_arn,
            description="Database credentials secret ARN",
        )
