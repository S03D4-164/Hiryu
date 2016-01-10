function visNetwork(nodes, edges){
    var container = document.getElementById('network');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = visOption();
    var network = new vis.Network(container, data, options);
    return network;
};


function visOption(){

    var options ={
        "autoResize": true,
        "configure": {
                "enabled": false,
                //"filter": 'nodes,edges',
                //"showButton": true
        },
        "nodes": {
                "borderWidth": 0.1,
                "scaling":{
                        "label": {
                                "enabled": true,
                        },
                },
                "shadow": true,
                "color":{
                    "background":"white",
                },
                "physics":true,
        },
        "groups":{
            "IP":{
                shape: 'icon',
                icon:{
                    code:'\uf233',
                },
            },
            "Organization":{
                shape: 'icon',
                icon:{
                    code:'\uf1ad',
                    color:'green',
                },
                color:'green',
            },
            "Registrant":{
                shape: 'icon',
                icon:{
                    code:'\uf007',
                    color:'grey',
                },
                color:'grey',
            },
        },
        "edges":{
                "arrows": 'to',
                "scaling":{
                        "label": {
                                "enabled": true,
                        },
                },
                //"shadow": true,
                "smooth": {
                        //"roundness": 0.1
                },
                "width":2,
                //"physics":false,
        },
        "interaction":{
                "hideEdgesOnDrag": false,
                "hover": false,
                "keyboard": true,
                "navigationButtons": true,
        },
        "physics": {
                enabled: true,
                //"solver": "forceAtlas2Based",
                //"solver": "barnesHut",
                "solver": "repulsion",
                barnesHut: {
                    gravitationalConstant:-2000,
                    centralGravity:0.4,
                    springLength: 150,
                    //springConstant: 0.02,
                    //damping: 0.1,
                    avoidOverlap: 0.1,
                },
                repulsion: {
                    nodeDistance: 150,
                    centralGravity:0.5,
                    springLength: 100,
                },
                forceAtlas2Based:{  
                    gravitationalConstant:-50,
                    centralGravity:0.01,
                    springLength:150,
                    avoidOverlap:0.1,
                },
                //"minVelocity":1,
        },
        //"manipulation": {
        //      "enabled": false,
        //},
    };
    return options;
};
