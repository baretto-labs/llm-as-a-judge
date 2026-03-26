docker run --rm \
-v "$(pwd)/demo:/home/marp/app" \
marpteam/marp-cli \
SLIDES.md --html --output SLIDES.html
[  INFO ] Converting 1 markdown...
[  INFO ] SLIDES.md => SLIDES.htmlSystem.out.println("Je pense que c'est dû au fait que les questions Neo4j sont
traitées en batch séparé.");



./run-benchmarks.sh --source-dir /Users/mehdi/Workspaces/Labs/OllamAssist/src/main/java --scenario "knn-only|hybrid,hybrid|hybrid,hybrid|hybrid-graph" 