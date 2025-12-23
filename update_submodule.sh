echo "Current branch: $(git branch --show-current)"

echo "Pulling latest changes"
git pull

echo "Updating submodules and applying patches"

git submodule sync
git submodule update --init --recursive