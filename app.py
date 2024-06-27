#!/usr/bin/env python3
import os

import aws_cdk as cdk

from serverless_rest_cdk.serverless_rest_cdk_stack import PyRestApiStack


app = cdk.App()
PyRestApiStack(app, "PyRestApiStack")

app.synth()
