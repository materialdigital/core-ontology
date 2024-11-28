function getElements(id){
    foundElements = []
    let entity = document.getElementById(id);
    if(entity !== undefined){
	foundElements.push(entity)
    }
    let elements = document.querySelectorAll('#overview li a[title="' + id + '"]');
    for (element of elements) {
	foundElements.push(element.parentElement);
    }

    let crossrefElements = document.querySelectorAll('#crossref div li a[title="' + id + '"]');
    for (element of crossrefElements) {
	foundElements.push(element.parentElement);
    }

    return foundElements;
}

function addOnClick(id) {
    /* adds onClick-Event to crosslinks to unhide hidden elements on click */

    let crossLinks = document.querySelectorAll('div dl dd a[title="' + id + '"]');
    for (link of crossLinks) {
	link.setAttribute("onclick", "expertMode()");
    }
}

function hideElement(id) {
    let elements = getElements(id);
    for (element of elements) {
	element.style.display = "none";
    }
    addOnClick(id);
}

function unhideElement(id) {
    let elements = getElements(id);
    for (element of elements) {
	displayFormat = (element.tagName == "LI")
	    ? "inline-block"
	    : "block";
	element.style.display = displayFormat;
    }
}

function handleChange(checkbox) {
    if(checkbox.checked === true) {
        expertMode();
    }else {
        standardMode();
    }

}

function addViewSwitch() {
    addStylesheet();
    slider = document.createElement("div");
    slider.classList.add("switchWithLabel");
    label1 = document.createElement("label");
    label1.classList.add("cell");
    label1.setAttribute("title", "Use Standard-View to see only classes and properties meant for modeling");
    label1.textContent = "Standard"
    label2 = document.createElement("label");
    label2.classList.add("cell")
    label2.setAttribute("title", "Use Expert View to see in addition parent classes meant for interoperability");
    label2.textContent = "Expert"
    sliderElement = document.createElement("label");
    sliderElement.classList.add("switch");
    explanation = "The standard view shows all the classes and properties meant to model scientific processes with m4i.";
    explanation += " To see also parent elements introduced for interoperability, choose expert view."
    sliderElement.setAttribute("title", explanation);
    input = document.createElement("input");
    input.setAttribute("type", "checkbox");
    input.setAttribute("id", "viewSlider");
    input.setAttribute("onchange", "handleChange(this)")
    label = document.createElement("span");
    label.classList.add("slider");
    label.classList.add("round");
    sliderElement.appendChild(input);
    sliderElement.appendChild(label);
    slider.appendChild(label1);
    slider.appendChild(sliderElement);
    slider.appendChild(label2);
    let overview = document.querySelector("#overview p");
    overview.textContent = overview.textContent + " " +  explanation;
    overview.appendChild(slider);
    let crossref = document.getElementById('crossref');
    explanationP = document.createElement("p");
    explanationP.textContent = explanation;
    crossref.insertBefore(explanationP, crossref.children[1]);
    }

    function addStylesheet(){
        const stylesheet = document.createElement("style");
        stylesheet.innerHTML = `
        .warning {
          background-color: #ffffcc;
          font-style:italic;
        }
        .switchWithLabel {
            position:fixed;
            right:2px;
            top:150px;
            display:table;
            background-color:white;
            border-radius: 26px;
            border: 2px solid #005A9C;
            padding-left: 5px;
            padding-right: 5px;
            height:40px;
            font-size:10pt;
            }
            
            .cell {
            display:table-cell;
            vertical-align:middle;
            height: 34px;
            color: #005A9C;
            }
            
            .switch {
              position: relative;
              display: inline-block;
              margin:4px;
              width: 60px;
              height: 34px;
            }
            
            /* Hide default HTML checkbox */
            .switch input {
              opacity: 0;
              width: 0;
              height: 0;
            }
            
            /* The slider */
            .slider {
              position: absolute;
              cursor: pointer;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background-color: #ccc;
              -webkit-transition: .4s;
              transition: .4s;
            }
            
            .slider:before {
              position: absolute;
              content: "";
              height: 26px;
              width: 26px;
              left: 4px;
              bottom: 4px;
              background-color: white;
              -webkit-transition: .4s;
              transition: .4s;
            }
            
            input:checked + .slider {
              background-color: #005A9C;
            }
            
            input:focus + .slider {
              box-shadow: 0 0 1px #005A9C;
            }
            
            input:checked + .slider:before {
              -webkit-transform: translateX(26px);
              -ms-transform: translateX(26px);
              transform: translateX(26px);
            }
            
            /* Rounded sliders */
            .slider.round {
              border-radius: 34px;
            }
            
            .slider.round:before {
              border-radius: 50%;
            }
            `
            document.querySelector('head').appendChild(stylesheet);
    
    }
    

function expertMode() {
    let ids = getAllUnusedElements();
    for (id of ids) {
	unhideElement(id);
    }
    document.getElementById('viewSlider').checked = true;
}


function standardMode() {
    let ids = getAllUnusedElements();
    for (id of ids) {
	hideElement(id);
    }
    document.getElementById('viewSlider').checked = false;
}

function addWarnings() {
    let ids = getAllUnusedElements();
    for (id of ids) {
	addWarning(id);
    }
}

function addWarning(id) {
    childs = document.getElementById(id).children;
    for (let i = 0; i < childs.length; i++) {
	if(childs[i].className === "comment") {
	    warning = document.createElement("p");
	    warning.classList.add("warning");
	    warning.id = id + "_warning";
	    warning.textContent = "This element is a parent element that is not intended to use for modeling, but only for interoperability with other ontologies."
	    if(!document.getElementById(id + "_warning")) {
		childs[i].insertBefore(warning, childs[i].children[0]);
	    }
	}
    }
    
}


function getAllUnusedElements(){

    elements = [];
    elements.push("http://www.w3.org/ns/prov#Activity");
    elements.push("http://purl.obolibrary.org/obo/BFO_0000017"); //realizable entity
    elements.push("http://purl.obolibrary.org/obo/BFO_0000015"); //process
    elements.push("https://schema.org/Intangible");
    elements.push("http://purl.obolibrary.org/obo/RO_0000057"); //has participant
    elements.push("http://xmlns.com/foaf/0.1/Agent");
    elements.push("http://xmlns.com/foaf/0.1/Organization");
    elements.push("http://xmlns.com/foaf/0.1/Person"); 
    elements.push("http://www.w3.org/ns/ssn/implements");
    elements.push("http://www.w3.org/ns/ssn/implementedBy");

    return elements;
}

$(document).ready(function() { addWarnings(); addViewSwitch(); standardMode(); });
