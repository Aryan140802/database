function queues(data, tagname) {
    count = 1;
    var tcount = 0;
    tagn = document.getElementById(tagname);
    table = document.createElement('table');
    console.log(data);

    var emptyarr = new Array(), totaldead, emptyarr2 = new Array(), totaln, totalre = data["servers"].length, arrtotalre = new Array(totalre).fill(0);
    console.log(arrtotalre);
    for (var i in data) {
        console.log(i, data[i]);
        if (i == "servers") {
            tr = document.createElement('tr');
            th = document.createElement('th');
            th.innerHTML = "QUEUE MANAGERS";
            tr.appendChild(th);
            th = document.createElement('th');
            th.innerHTML = "QUEUES";
            tr.appendChild(th);
            for (var j of data[i]) {
                th = document.createElement('th');
                th.innerHTML = j;
                tr.appendChild(th);
            }
            table.appendChild(tr);
        }
        else if (i != "layer") {
            td = document.createElement('td');
            td.innerHTML = i;
            console.log(count, i, data[i]);
            for (var j in data[i]) {
                tr = document.createElement('tr');
                td1 = document.createElement('td');
                console.log(j);
                td1.innerHTML = j;
                tr.appendChild(td1);
                var dl = data[i][j].length;
                var earrlen = emptyarr.length;
                console.log(dl, earrlen, data[i][j], emptyarr);

                // Modified logic for exception queues
                if (tagname === "except") {
                    // For exception queues, just sum all numeric values
                    arrtotalre = arrtotalre.map((a, tre) => {
                        let val = data[i][j][tre];
                        return !isNaN(val) ? a + parseInt(val) : a;
                    });
                } 
                else {
                    // Original logic for other queue types
                    if (j == "DEAD_LETTER") {
                        if (earrlen == 0) {
                            emptyarr = data[i][j];
                        }
                        else {
                            var currentvalue, currenta;
                            emptyarr = emptyarr.map((a, deadletter) => {
                                currentvalue = data[i][j][deadletter].split(":")[0];
                                if (typeof (a) == "string") {
                                    currenta = a.split(":")[0];
                                }
                                else {
                                    currenta = a;
                                }
                                if (!isNaN(currentvalue)) {
                                    currentvalue = parseInt(currentvalue);
                                    if (!isNaN(currenta)) {
                                        currenta = parseInt(currenta);
                                    }
                                    return currenta + currentvalue;
                                }
                                else {
                                    return currenta;
                                }
                            });
                        }
                    }
                    var earrlen2 = emptyarr2.length;
                    if (j == "APIDB_DPG_N") {
                        if (earrlen2 == 0) {
                            emptyarr2 = data[i][j];
                        }
                        else {
                            var currentvalue, currenta;
                            emptyarr2 = emptyarr2.map((a, apin) => {
                                currentvalue = data[i][j][apin].split(":")[0];
                                if (typeof (a) == "string") {
                                    currenta = a.split(":")[0];
                                }
                                else {
                                    currenta = a;
                                }
                                if (!isNaN(currentvalue)) {
                                    currentvalue = parseInt(currentvalue);
                                    if (!isNaN(currenta)) {
                                        currenta = parseInt(currenta);
                                    }
                                    return currenta + currentvalue;
                                }
                                else {
                                    return currenta;
                                }
                            });
                        }
                    }
                    arrtotalre = arrtotalre.map((a, tre) => !isNaN(data[i][j][tre]) ? a + data[i][j][tre] : a);
                }

                console.log(emptyarr, arrtotalre);
                for (var k of data[i][j]) {
                    k = k.toString().split(":");
                    console.log("current value:", k[0], "previous value:", k[1]);
                    td2 = document.createElement('td');
                    if (k[0] == 'None') {
                        td2.innerHTML = "";
                    }
                    else {
                        td2.innerHTML = k[0];
                        if (j == "DEAD_LETTER") {
                            tcount += 1;
                            console.log(i, j, k, tcount);
                        }
                    }
                    console.log(j, k);

                    tr.appendChild(td2);
                    if (tagname == "dbqueue" && k[0] > 5000) {
                        console.log(j, data[i][j].indexOf(k));
                        var indexdata = data[i][j].indexOf(k);
                        problemc += 1;
                        problems.push("Server " + data["servers"][indexdata] + "  :  " + i + "  :  " + j + "  :  " + k);
                    }
                    if (tagname == "dbqueue" && k[0] > 0) {
                        td2.style.backgroundColor = "#f58608";
                        console.log(k[0], k[1]);
                        if (k[1] && k[0] > k[1]) {
                            td2.innerHTML += "  &uarr;";
                        }
                        else if (k[1] && k[0] < k[1]) {
                            td2.innerHTML += "  &darr;";
                        }
                    }
                }
                console.log(i, ":", j, ":", data[i][j]);

                table.appendChild(tr);
            }
            tagn.appendChild(table);
            var trs = tagn.getElementsByTagName('tr');
            console.log(trs);
            console.log(trs[count], trs, count);
            trs[count].insertBefore(td, trs[count].firstChild);
            count += Object.keys(data[i]).length;
            td.rowSpan = Object.keys(data[i]).length;
        }
    }
    console.log(count, tcount);
    console.log(totaldead, totaln);
    if (tagname == "dbqueue") {
        function total(totaldata, txt) {
            tr = document.createElement('tr');
            tr.id = "total";
            tr.style.backgroundColor = "rgb(40 2 79)";
            if (txt == "DEAD_LETTER") {
                td = document.createElement('td');
                td.innerHTML = "TOTAL";
                td.rowSpan = "2";
                tr.appendChild(td);
            }
            td = document.createElement('td');
            td.innerHTML = txt;
            tr.appendChild(td);
            console.log(totaldata);
            for (var t in totaldata) {
                console.log(typeof (totaldata), totaldata[t]);
                td = document.createElement('td');
                td.innerHTML = totaldata[t];
                tr.appendChild(td);
            }
            table.appendChild(tr);
            tagn.appendChild(table);
        }

        total(emptyarr, "DEAD_LETTER");
        total(emptyarr2, "APIDB_DPG_N");
    }
    else {
        tr = document.createElement('tr');
        tr.style.backgroundColor = "rgb(40 2 79)";
        td = document.createElement('td');
        td.innerHTML = "";
        tr.appendChild(td);
        td = document.createElement('td');
        td.innerHTML = "Total";
        tr.appendChild(td);
        for (var t in arrtotalre) {
            td = document.createElement('td');
            td.innerHTML = arrtotalre[t];
            tr.appendChild(td);
        }

        table.appendChild(tr);
        tagn.appendChild(table);
    }
    console.log(arrtotalre);
}
