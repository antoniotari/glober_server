#!/usr/bin/python
# -*- coding: utf-8 -*-
from py4j.java_gateway import JavaGateway
gateway = JavaGateway()
gateway.entry_point.SendPush('and',"5702","5702",'d','essage')
