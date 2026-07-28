
# prepare left side (old release)
java -jar /Users/joerg/robot.jar remove --input  ../../../../pmdco.owl  --select rdfs:label=@de remove --term-file terms.txt --output left.owl

# prepare right side (new make result)
java -jar /Users/joerg/robot.jar remove --input  ../../pmdco.owl --select rdfs:label=@de remove --term-file terms.txt  --output right.owl

# gen diff
java -jar /Users/joerg/robot.jar diff --left left.owl --right right.owl --labels true --format markdown --output diff.md