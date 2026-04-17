PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

DELETE {
    ?prop owl:propertyChainAxiom ?chain .
}
WHERE {
    ?prop owl:propertyChainAxiom ?chain .
}
