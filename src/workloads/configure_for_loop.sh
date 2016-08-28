#!/bin/bash


sudo sysctl -w net.ipv4.tcp_allowed_congestion_control="reno cubic"
sudo sysctl -w net.ipv4.tcp_available_congestion_control="reno cubic"
sudo sysctl -w net.ipv4.tcp_congestion_control="reno"
