#!/bin/bash

git status
git add *
git commit -m "third commit"
git branch -M main
git push -u origin main
