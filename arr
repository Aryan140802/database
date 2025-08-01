document.addEventListener("DOMContentLoaded",async ()=> {
var uid=localStorage.getItem('uidd');
var password=localStorage.getItem('password');
  try{
     const response  = await fetch('https://10.191.171.12:5443/PyPortal/EISHome/authenticatePortal/',{
     method:'POST',
     headers:{
             'Content-Type':'application/json',
    },
    body: JSON.stringify({uid,password})
    });
    const data = await response.json();
    if(data.status==302){
            console.log("login successfull");
	    const redirectUrl=localStorage.getItem("redirectafterlogin");
	    if (redirectUrl){
		localStorage.removeItem("redirectafterlogin");
		window.location.href=redirectUrl;
	    }
    }
    else{
	    console.log(data.status)
	    localStorage.setItem("redirectafterlogin",window.location.href);
          window.location.href='https://10.191.171.12:5443/PyPortal/';
    }
  }
catch(e){
console.log("an error occured for login"+e)

}
});




var xhttp = new XMLHttpRequest();
xhttp.open("GET","./data/datetime", false);
xhttp.send()
var datat = xhttp.responseText.split("\n");
console.log(datat)

xhttp.open("GET","./data/data_h/notupdatedfiles", false);
xhttp.send()
var datafile = xhttp.responseText.split("\n");
console.log(datafile)


document.getElementsByTagName("p")[0].innerHTML+=datat[0]
import datadbq from "./data/mq/dbq.json" with { type: "json" };
import datadbr from "./data/mq/retry.json" with { type: "json" };
import datadbe from "./data/mq/exception.json" with { type: "json" };
import datapaye from "./data/mq/PAY_EXP.json" with { type: "json" };
import datapays from "./data/mq/PAY_SYS.json" with { type: "json" };
import datawin from "./data/WIN.json" with { type: "json" };
import datamisce from "./data/mq/MISC_EXP.json" with { type: "json" };
import datamiscs from "./data/mq/MISC_SYS.json" with { type: "json" };
import dataivre from "./data/mq/IVR_EXP.json" with { type: "json" };
import dataivrs from "./data/mq/IVR_SYS.json" with { type: "json" };
import dataacc from "./data/mq/ACCN_SYS.json" with { type: "json" };
import datamem from "./data/mq/memory.json" with { type: "json" };
import dataloge from "./data/mq/LOG_EXP.json" with { type: "json" };
import datalogs from "./data/mq/LOG_SYS.json" with { type: "json" };
import dataaccn from "./data/mq/ACCN_EXP.json" with { type: "json" };
import datacusts from "./data/mq/CUST_SYS.json" with { type: "json" };
import datacuste from "./data/mq/CUST_EXP.json" with { type: "json" };
import dataaadhare from "./data/mq/AADHAR_EXP.json" with { type: "json" };
import dataaadhars from "./data/mq/AADHAR_SYS.json" with { type: "json" };
import datang from "./data/mq/NG5.json" with { type: "json" };

var problems=[],problemc=0,arrdata,file,arrlen;
var th,td,tr,td1,tagn,td2,count=1,table, dbqtag=document.getElementById("dbqueue");
if(datafile.length >5){
	problemc+=1
	problems.push("check data ")
}
else{
	for(var arr of datafile){
 		console.log(arr)
		arrdata=arr.split(" ");
		console.log(arrdata)
		arrlen=arrdata.length
		// ['data_h', 'Sep', '05', '13:29', 'mq_n_63.json']
		if(arrdata[0]=='data_h'){
			problemc+=1
 			problems.push("check "+arrdata[arrlen-1] )
		}
		else if(arrdata[0]=='data'){
			file=arrdata[arrlen-1].split("_")
			problems.push(file[2]+" last updated on:"+arrdata[1],arrdata[2],arrdata[3])
			problemc+=1
		}
	}
}

function queues(data,tagname){
	count=1;
	var tcount=0;
	tagn=document.getElementById(tagname);
	table=document.createElement('table');
	console.log(data)

	var emptyarr=new Array(),totaldead,emptyarr2=new Array(),totaln,totalre=data["servers"].length,arrtotalre=new Array(totalre).fill(0);
	console.log(arrtotalre);
	for(var i in data){
		console.log(i,data[i])
		if(i == "servers"){
			tr=document.createElement('tr');
			th=document.createElement('th');
			th.innerHTML="QUEUE MANAGERS"
			tr.appendChild(th)
			th=document.createElement('th');
			th.innerHTML="QUEUES";
			tr.appendChild(th)
			for(var j of data[i]){
				th=document.createElement('th');
				th.innerHTML=j
				tr.appendChild(th)
			}
 			table.appendChild(tr)
		}
		else if(i != "layer"){
			td=document.createElement('td');
			td.innerHTML=i;
			console.log(count,i,data[i])
			for(var j in data[i]){
				 tr=document.createElement('tr');
 				td1=document.createElement('td');
				console.log(j)
				td1.innerHTML=j;
				tr.appendChild(td1)
				var dl=data[i][j].length
				var earrlen=emptyarr.length
				console.log(dl,earrlen,data[i][j],emptyarr)
				if(j == "DEAD_LETTER"){

					if(earrlen == 0){
						emptyarr=data[i][j];
					}
					else{
						var currentvalue,currenta;
						emptyarr= emptyarr.map((a, deadletter) =>{
							currentvalue=data[i][j][deadletter].split(":")[0]
							if(typeof(a) == "string"){
                    						currenta=a.split(":")[0]}
                    					else{
                        					currenta=a

                    					}
							if(!isNaN(currentvalue) ){
								currentvalue=parseInt(currentvalue)
								if(!isNaN(currenta) ){
								currenta=parseInt(currenta);
								}
								return currenta + currentvalue;
							}
							else{
								return currenta;

							}
						});
					}
				}
 				var earrlen2=emptyarr2.length
				if(j == "APIDB_DPG_N"){
					if(earrlen2 == 0){
                                                 emptyarr2=data[i][j];
                                         }
                                         else{
                                                 var currentvalue,currenta;
                                                 emptyarr2= emptyarr2.map((a, apin) =>{
                                                         currentvalue=data[i][j][apin].split(":")[0]
                                                         if(typeof(a) == "string"){
                                                                 currenta=a.split(":")[0]}
                                                         else{
                                                                 currenta=a

                                                         }
                                                         if(!isNaN(currentvalue) ){
                                                                 currentvalue=parseInt(currentvalue)
                                                                 if(!isNaN(currenta) ){
                                                                 currenta=parseInt(currenta);
                                                                 }
                                                                 return currenta + currentvalue;
                                                         }
                                                         else{
                                                                 return currenta;

                                                         }
                                                 });
                                         }

				}
				arrtotalre= arrtotalre.map((a, tre) => !isNaN( data[i][j][tre]) ? a + data[i][j][tre]:a)
				console.log(emptyarr,arrtotalre)
				for(var k of data[i][j]){
					k=k.split(":")
					console.log("current value:", k[0],"previous value:",k[1])
 					td2=document.createElement('td');
					if(k[0] == 'None'){
 						td2.innerHTML="";;
					}
					else{
						td2.innerHTML=k[0];
						if(j == "DEAD_LETTER"){
							tcount+=1
							console.log(i,j,k,tcount)
						}
					}
					console.log(j,k)

					tr.appendChild(td2)
					if(tagname == "dbqueue" && k[0] > 5000 ){
						console.log(j,data[i][j].indexOf(k[0]));
						var indexdata=data[i][j].indexOf(k[0]);
						problemc+=1;
						problems.push("Server "+data["servers"][indexdata]+"  :  "+i+"  :  "+j+"  :  "+k)
					}
					if(tagname == "dbqueue" && k[0] > 0 ){
						//td2.style.backgroundColor="rgb(20 153 22)"
						td2.style.backgroundColor="#f58608"
						console.log(k[0],k[1])
						if(k[0] > k[1]){

							td2.innerHTML+="  &uarr;";
						}
						else if(k[0] < k[1]){

							td2.innerHTML+="  &darr;";
						}
					}
				}
				console.log(i,":",j,":",data[i][j])

				table.appendChild(tr)
			}
			tagn.appendChild(table)
			var trs=tagn.getElementsByTagName('tr');
			console.log(trs)
			console.log(trs[count],trs,count)
			trs[count].insertBefore(td,trs[count].firstChild);
			count+=Object.keys(data[i]).length;
			td.rowSpan=Object.keys(data[i]).length;
		}
	}
	console.log(count,tcount)
	console.log(totaldead,totaln)
	if(tagname == "dbqueue"){

		function total(totaldata,txt){
			tr=document.createElement('tr');
			tr.id="total"
			tr.style.backgroundColor="rgb(40 2 79)"
			if(txt == "DEAD_LETTER"){
				td=document.createElement('td');
				td.innerHTML="TOTAL"
				td.rowSpan="2"
//td.backgroundColor="#43097d";
				tr.appendChild(td)
			}
			td=document.createElement('td');
			td.innerHTML=txt
			tr.appendChild(td)
			console.log(totaldata);
			for(var t in totaldata){
				console.log(typeof(totaldata), totaldata[t])
				td=document.createElement('td');
				td.innerHTML=totaldata[t]
				tr.appendChild(td)
			}
			table.appendChild(tr)
			tagn.appendChild(table)
		}

//total(totaldead,"DEAD_LETTER");
		total(emptyarr,"DEAD_LETTER");
		total(emptyarr2,"APIDB_DPG_N");
	}
	else{
		tr=document.createElement('tr')
		tr.style.backgroundColor="rgb(40 2 79)"
		td=document.createElement('td');
		td.innerHTML=""
		tr.appendChild(td)
		td=document.createElement('td');
		td.innerHTML="Total"
		tr.appendChild(td)
		for(var t in arrtotalre){
			td=document.createElement('td');
			td.innerHTML=arrtotalre[t]
			tr.appendChild(td)
		}

		table.appendChild(tr)
	 	tagn.appendChild(table)
	}
	console.log(arrtotalre)
}

queues(datadbq,"dbqueue")
queues(datadbr,"retry")
queues(datadbe,"except")


/* DBTRANSMISSION QUEUE */
function dbtrans(data,tagnm){
	tagn=document.getElementById(tagnm)
	var newtag=document.createElement("div")
	newtag.className="divcontainer"
	for (var l of data){
		console.log(l)
		var newtag1=document.createElement("div")
		newtag1.className="card"
		table=document.createElement('table');
		for(var i in l){
  			console.log(i,data[i])
	 		if(i == "layer"){
				var h = document.createElement('h3');
				h.innerHTML=l[i];
				newtag1.appendChild(h)

			}
			else if(i == "servers" || i == "mq"){
				tr=document.createElement('tr');
				th=document.createElement('th');
				th.innerHTML="QUEUES"
				tr.appendChild(th)
 				for(var j of l[i]){
					console.log(j)
					th=document.createElement('th');
					th.innerHTML=j
					tr.appendChild(th)
				}
 				table.appendChild(tr)
 			}
			else if(i != "layer"){
 				td=document.createElement('td');
				td.innerHTML=i;
				tr=document.createElement('tr');
 				tr.appendChild(td)
				for(var j of l[i]){
					td1=document.createElement('td');
					console.log(j)
					if(i == "CHANNELS"){
						if(j == "RUNNING"){
							td1.innerHTML="&#9989;"
						}
						else if(j == "STOPPED" || j == "stopped" ){
							td1.innerHTML="&#10060;"
							problemc+=1;
							problems.push(j)
						}else{ 
							td1.className="show"
							td1.innerHTML="&#10071;"+`<span class="hide">`+j+`</span>`;
							console.log(j)
							problemc+=1
							problems.push(j)
						}
					}
					else
					{
						if(tagnm == "Disk"){
							if(j > 0){
 								td1.innerHTML="&#9989"
							}
							else if(j = 0){td1.innerHTML="&#10060;";
								problemc+=1;
								 problems.push(i,j)
							}
							else{td1.innerHTML="";
							}
						}else{
							if(j == 'None'){
								td1.innerHTML="";
							}
							else{
								if(j> 70 ){
									problemc+=1;
									problems.push("Server "+l["servers"][l[i].indexOf(j)]+" => "+i+" => "+j)
								}
								td1.innerHTML=j;
								}
						}
					}
					tr.appendChild(td1)
					table.appendChild(tr)
 				}

			}
		}
 		if(tagnm != "Disk"){
 			newtag1.appendChild(table)
			newtag.appendChild(newtag1)}
		else{
			tagn.appendChild(table)
		}
	}
	console.log(data,tagnm)
	if(tagnm != "Disk"){
  		tagn.appendChild(newtag)}
	else{
		tagn.appendChild(table)
	}
}

dbtrans([datacuste,datacusts],"dbtransmission");
dbtrans([dataloge,datalogs],"dbtransmission");
dbtrans([datapaye,datapays],"dbtransmission");
dbtrans([dataaadhare,dataaadhars],"dbtransmission");
dbtrans([dataaccn,dataacc],"dbtransmission");
dbtrans([datamisce,datamiscs],"dbtransmission");
dbtrans([dataivre,dataivrs],"dbtransmission");
dbtrans([datawin,datang],"dbtransmission");
dbtrans([datamem,0],"Disk");

/* GRAPH VISUALISATION */
document.getElementById("dbqueue").innerHTML+=`<div class="card"><canvas id="myChart" height="3%" width="5%" style="margin-left:5%"></canvas></div>`
import data from "./data/dataset.json" with { type: "json" };
var ctx =document.getElementById('myChart').getContext('2d');
var gradientbg=ctx.createLinearGradient(0,0,0,870);
gradientbg.addColorStop(0,'#7520c9')
gradientbg.addColorStop(1,'rgba(0,0,0,0)')
//gradientbg.addColorStop(2,'#1435db')
//gradientbg.addColorStop(3,'rgba(0,0,0,0)')

var datasetdata=data;
var myChart=new Chart("myChart", {
	type: "bar",
  	data:datasetdata,
  	options: {
		animations: {
      			radius: {
        			duration: 400,
        			easing: 'linear',
        			loop: (context) => context.active
      			}
    		},
    		legend: {display: true},
    		scales: {
      			yAxes: [{
        			ticks: { beginAtZero: true,
                    			fontColor: 'white',
					callback: function(value){return value+ "%"}
				},
				gridLines: {
                			display:false
            			}
      			}],
 			xAxes: [{
         			ticks: { beginAtZero: true,
                    			fontColor: 'white'},
         			gridLines: {
                 		display:false
             			}
       			}],
    		},
		title: {
        		display: true,
        		text: ' Disk Utilization',
  		} 
	}
});
console.log(myChart.data.datasets[4].backgroundColor)
console.log(data)
var dsl;
for(var ds in data.datasets){
	console.log(data.datasets[ds].label,data.datasets[ds].data)
	for(var dd of data.datasets[ds].data){
		console.log(dd)
		dsl=data.datasets[ds].data.indexOf(dd)
		if(data.datasets[ds].label == "Free Memory" && dd < parseInt(15) ){
			console.log(dd)
			problemc+=1;
			problems.push("Server "+data.labels[dsl]+" => "+data.datasets[ds].label+" => "+dd+"% ")
		}
		else if(data.datasets[ds].label != "Free Memory" && dd > 70){
			 problemc+=1;
			problems.push("Server "+data.labels[dsl]+" => "+data.datasets[ds].label+" => "+dd+"% ")
		}
	}
}
myChart.data.datasets[4].backgroundColor=gradientbg
myChart.data.datasets[4].type="line"
myChart.update()
var ndata;
console.log(problems)
var badge=document.getElementById('badge');
badge.innerHTML=problemc;
var pl, plen=0
ndata=`<span class="hide">`
for(var p of problems){
	ndata+=p+`</br>`;
}
ndata+=`</span>`;
console.log(plen)
 badge.innerHTML+=ndata
badge.className="show"

