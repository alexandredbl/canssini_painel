function temperature_graph(dataobj) {
    const ctx = document.getElementById('temperature_graph');   
    const data = {
        datasets: [{
            label: 'T / ºC',
            data: dataobj,
            showLine: true,
            borderColor: "#f80",
            tension: 0.1,
        }]
    };
    return new Chart(ctx, {
        type: 'scatter',
        data: data,
        options: {
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });
}
function pressure_graph(dataobj) {
    const ctx = document.getElementById('pressure_graph');   
    const data = {
        datasets: [{
            label: 'P / hPa',
            data: dataobj,
            showLine: true,
            tension: 0.1,
            borderColor: "#08f",
        }]
    };
    return new Chart(ctx, {
        type: 'scatter',
        data: data,
        options: {
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });
}
function altitude_graph(t,h1,h2) {
    const ctx = document.getElementById('altitude_graph');   
    const data = {
        datasets: [
            {
                label: 'h_Altímetro / m',
                data: h1,
                fill: false,
                borderColor: '#f80',
                tension: 0.1,
                showLine: true,
            },
            {
                label: 'h_GPS / m',
                data: h2,
                fill: false,
                borderColor: '#08f',
                tension: 0.1,
                showLine: true,
            }
        ]
    };
    return new Chart(ctx, {
        type: 'scatter',
        data: data,
        options: {
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });
}

function updatePTgraph(dataobj,PTgraph) {
    PTgraph.data.datasets[0].data = dataobj;
    PTgraph.update();
}
function updatehgraph(h1,h2,hgraph) {
    hgraph.data.datasets[0].data = h1;
    hgraph.data.datasets[1].data = h2;
    hgraph.update();
}

let T_graph = temperature_graph([]);
let P_graph = pressure_graph([])
let h_graph = altitude_graph([],[])