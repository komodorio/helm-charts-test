# How to work with this `helm-charts-test` repository

1. Clone this repository
2. Add the original helm-chart repo as upstream
```bash
git remote add upstream git@github.com:komodorio/helm-charts.git 
```
3. fetch the upstream
```bash
git fetch upstream 
```
4. Update master branch
```bash
git checkout master
git merge upstream/master
```
5. Create a new branch for your changes
```bash
git checkout -b BRANCH_NAME
```
6. In case you want to check a change in the upstream, you can merge it to your branch
```bash 
git merge upstream/BRANCH_NAME
```