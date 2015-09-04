var instance = openerp.init(["web"]); // get a new instance
instance.session.session_bind(); // bind it to the right hostname
var widget1 = new instance.web.Widget();
var stock = new instance.web.Model('stock.move');
var mrp = new instance.web.Model('mrp.production');
var cat = new instance.web.Model('product.category');
var polizdelki=new Array();
var izdelki=new Array();
var kategorije=new Array();
var dblist;
var rId;
var cId;
var relacija;
var vrstaIzdelka;
var sGotovo;
var userID;
var basketLocked = 0;
var tipZakljucka;
//Funkcija se izvede na page load in definira web/dialog page , ki jih potrebujem za vnos kolicin in 
//definira 'on click' evente.
$(function() {

	//jQuery("#mysearch").jqGrid('filterGrid','#grid2',{
	//});
	
	//Napolnim seznam podjetij (baz) za login screen
	widget1.rpc("/web/database/get_list",{}).then(function(result){dblist=result;fillPodjetja();},function(result){alert("Napaka")});	
	function fillPodjetja(){
		 
		var sel=document.getElementById("s1");
		for (i=0;i<dblist.length;i++){
			option1=document.createElement("option");
			option1.text=dblist[i];
			sel.add(option1,null);		
		}
	   	
	} 

	//Delovni nalogi - TESTO
	$( "#dialog-testo" ).dialog({
		autoOpen: false,
	    height: 250,
	    width: 510,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnDelno:{
	    		class: 'ui-button-red',
	      		text: ' Delno ',
	      		click: function() {
	    			testoFill("open");
	    		}	             
	   		},
          	btnZakljuci:{
          		class: 'ui-button-orange',
      			text: 'Zaključi',
      			click: function() {
    		  		testoFill("close");
    		  	}	             
          	},
          	btnPreklici:{
          		class: 'ui-button-gray',
      			text: 'Prekliči',
      			click: function() {
    		  		$( this ).dialog("close");
    			}	             
          	}
		}	      
	});
	//Delovni nalogi - Hladilnica
	$( "#dialog-hladilnica" ).dialog({
		autoOpen: false,
	    height: 250,
	    width: 510,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnDelno:{
	    		class: 'ui-button-red',
	      		text: ' Delno ',
	      		click: function() {
	    			hladilnicaFill("open");
	    		}	             
	   		},
          	btnZakljuci:{
          		class: 'ui-button-orange',
      			text: 'Zaključi',
      			click: function() {
    		  		hladilnicaFill("close");
    		  	}	             
          	},
          	btnPreklici:{
          		class: 'ui-button-gray',
      			text: 'Prekliči',
      			click: function() {
    		  		$( this ).dialog("close");
    			}	             
          	}
		}	      
	});
	
	//Delovni nalogi - OSNOVA
	$( "#dialog-polizdelki" ).dialog({
  		autoOpen: false,
  		height: 290,
  		width: 550,
  		position: "top",
  		modal: true,
  		buttons: {
  			btnDelno:{
	    		class: 'ui-button-red',
	      		text: ' Delno ',
	      		click: function() {
	    			polizdelkiFill("open");
	    		}	             
	   		},
	   		btnZakljuci:{
          		class: 'ui-button-orange',
      			text: 'Zaključi',
      			click: function() {
    		  		polizdelkiFill("close");
    		  	}	             
          	},
  			btnPreklici:{
          		class: 'ui-button-gray',
      			text: 'Prekliči',
      			click: function() {
    		  		$( this ).dialog("close");
    			}	             
          	}
		}	      
	});
	
	//Delovni nalogi - IZDELKI PEKA
	$( "#dialog-izdelki" ).dialog({
		autoOpen: false,
	    height: 340,
	    width: 505,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnDelno:{
	    		class: 'ui-button-red',
	      		text: ' Delno ',
	      		click: function() {
	    			izdelkiFill("open");
	    		}	             
	   		},
	   		btnZakljuci:{
          		class: 'ui-button-orange',
      			text: 'Zaključi',
      			click: function() {
    		  		izdelkiFill("close");
    		  	}	             
          	},
          	btnPreklici:{
          		class: 'ui-button-gray',
      			text: 'Prekliči',
      			click: function() {
    		  		$( this ).dialog("close");
    			}	             
          	}
		}	      
	});
	
	//Relacije - NALOŽI VSE
	$( "#dialog-all" ).dialog({
		autoOpen: false,
	    height: 250,
	    width: 500,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnPotrdi:{
	    		class: 'ui-button-orange',
	      		text: 'Potrdi',
	      		click: function() {
	      			basketFillAll(); 0
	      			$( this ).dialog( "close" );
            	}	             
	    	},
	    	btnPreklici:{
	    		class: 'ui-button-gray',
	      		text: 'Prekliči',
	      		click: function() {
	            	$( this ).dialog( "close" );
	          	},	             
	      	},
		}	      
	});
	
	//Relacije - NALOŽI DELNO
	$( "#dialog-partial" ).dialog({
		autoOpen: false,
	    height: 250,
	    width: 530,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnDelno:{
	    		class: 'ui-button-red',
	      		text: ' Delno ',
	      		click: function() {
	      			basketFillPartial("open");
	    		}	             
	   		},
	   		btnZakljuci:{
          		class: 'ui-button-orange',
      			text: 'Zaključi',
      			click: function() {
      				basketFillPartial("close");
    		  	}	             
          	},
          	btnPreklici:{
          		class: 'ui-button-gray',
      			text: 'Prekliči',
      			click: function() {
    		  		$( this ).dialog("close");
    			}	             
          	}
		}	      
	});
	
	//Vnesena je bila manjsa kolicina kot narocena
	$( "#dialog-value-warning" ).dialog({
		autoOpen: false,
	    height: 290,
	    width: 505,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnPotrdi:{
	    		class: 'ui-button-orange',
	      		text: 'Potrdi',
	      		click: function() {
	      			var parent_call = $(this).data('parent');
	      			updateDBValues(parent_call); 0
	      			$( this ).dialog( "close" );
            	}	             
	    	},
	    	btnPreklici:{
	    		class: 'ui-button-gray',
	      		text: 'Prekliči',
	      		click: function() {
	            	$( this ).dialog( "close" );
	          	},	             
	      	},
		}	      
	});
	
	//Dialog za splosna opozorila, tekst nastavimo pred klicem open
	$( "#dialog-general-warning" ).dialog({
		autoOpen: false,
	    height: 260,
	    width: 505,
	    position: "top",
	    modal: true,
	    buttons: {
	    	btnPreklici:{
	    		class: 'ui-button-gray',
	      		text: 'Zapri',
	      		click: function() {
	            	$( this ).dialog( "close" );
	          	},	             
	      	},
		}	      
	});
	
	
	$( "#dialog-partner" ).dialog({
	      autoOpen: false,
	      height: 200,
	      width: 700,
	      position: "top",
	      modal: true,
	      buttons: {
	    	  "Zapri":function() {
	              $( this ).dialog( "close" );
	          },
	         
	      }	      
	  });
          
   $("#run").on("click",{gotovo:false},osveziGridBasket);
   $("#kon").on("click",{gotovo:true},osveziGridBasket);
   $("#izhodDn1").on("click",{divID:'outDn1'},izhod); 
   $("#runDn1").on("click",{gotovo:false},osveziGridDn1);
   $("#konDn1").on("click",{gotovo:true},osveziGridDn1);
   $("#izhod").on("click",{divID:'outGroup'},izhod); 
   $("#blogin").on("click",login); 
   $("#deliver").on("click",{rela:'Relacija 1'},deliver); 
   $("#deliver1").on("click",{rela:'Relacija 2'},deliver); 
   //$("#deliver2").on("click",{rela:'Relacija 3'},deliver); 
   $("#dn1").on("click",{kat:'Polizdelki_testo'},dn1); 
   $("#dn2").on("click",{kat:'Polizdelki'},dn1); 
   $("#dn3").on("click",{kat:'Izdelki'},dn1); 
   $("#dn4").on("click",{kat:'Dodelava'},dn1); 
   $("#hl1").on("click",{kat:'Hladilnica'},dn1); 
   $("#deliverall").on("click",{rela:'Relacija'},deliver); 
   $("#Exit").on("click",Exit);
   $("#grouping").on("click",groupingON);
                          
});

function groupingON(event){
	
	g2 = $("#grid1").jqGrid("getGridParam", "grouping");
	if (g2)
		$('#grid1').jqGrid('groupingRemove');
	else
		$('#grid1').jqGrid('groupingGroupBy', 'product_with_bom_name');
	
	//$('#grid1').jqGrid('groupingGroupBy', 'product_with_bom_name');
	//$('#grid1').jqGrid('groupingRemove');
	}


//odprem gride , glede na event data
function deliver(event){
	relacija=event.data.rela;
	$("#Header11").text('>   '+relacija);
	$("#select1").attr('class','Closed');	
	$("#outGroup").attr('class','Open');
	$("#grid2").jqGrid("GridUnload");
	initGridBasket();	
	$("#run").click();
	}
	
function dn1(event){
	vrstaIzdelka=event.data.kat;
	if (vrstaIzdelka == 'Polizdelki_testo'){
		$("#grouping").show();
	}
	else
		$("#grouping").hide();
	
	$("#Header12").text('>'+event.data.kat);	
	if (event.data.kat=='Izdelki'||event.data.kat=='Izdelki1'||event.data.kat=='Dodelava')
		kategorije=izdelki;
	else if (event.data.kat=='Hladilnica')
		kategorije=polizdelki.concat(izdelki);
		//kategorije=polizdelki;
	else 
		kategorije=polizdelki;
	$("#select1").attr('class','Closed');	
	$("#outDn1").attr('class','Open');
	$("#grid1").jqGrid("GridUnload"); 
	initGridDn1();	
	$("#runDn1").click();
}

//#blogin _ logira uporabnika in napolni array izdelkov in polizdelkov
function login (){		
    $("#blogin").css('color','red'); 
    so=document.getElementById("s1").selectedIndex;
    
    //----------ZA AVTO LOGIN V BAZO test-SG ---------//
    var pekarna_index = -1;
    for(i=0;i<document.getElementById("s1").length;i++){
    	if (document.getElementById("s1").options[i].text == 'test_SG')
    		pekarna_index = i;
    }
    if (document.getElementById("u").value == 'admin' && pekarna_index != -1){
    	so = pekarna_index;
    }
    //------------------------------------------------//
    
    //Prikaz podjetja in verzije
    $("#podjetje").text('Podjetje: ' + document.getElementById("s1").options[so].text + ', Verzija: v.03.27');
    
    openERP_user = '';
    if (document.getElementById("u").value == 'Testo-Polizdelki'){
    	openERP_user = '_testo';
    	$("#dn1").show(); 
    	$("#dn2").show();
    	$("#dn3").hide();
    	$("#dn4").hide();
    	$("#deliverall").show();
    	$("#deliver").hide();
    	$("#deliver1").hide();
    	$("#deliver2").hide();
    	$("#hl1").hide();
    	
    	$("#dv1").show();
    	$("#dv2").show();
    	$("#dv3").hide();
    	$("#dv4").hide();
    	$("#dv5").hide();
    	$("#dv6").hide();
    	$("#dv7").hide();
    	$("#dv8").show();
    	
    	$("#dhl1").hide();
    }
	else if (document.getElementById("u").value == 'Peka-Dodelava-Hladilnica'){
    	openERP_user = '_peka';
    	$("#dn1").hide();
    	$("#dn2").hide();
    	$("#dn3").show();
    	$("#dn4").show();
    	$("#deliverall").hide();
    	$("#deliver").hide();
    	$("#deliver1").hide();
    	$("#deliver2").hide();
    	$("#hl1").show();
    	
    	$("#dv1").hide();
    	$("#dv2").hide();
    	$("#dv3").show();
    	$("#dv4").show();
    	$("#dv5").hide();
    	$("#dv6").hide();
    	$("#dv7").hide();
    	$("#dv8").hide();
    	
    	$("#dhl1").show();
	}
	else if (document.getElementById("u").value == 'Košare'){
    	openERP_user = '_kosare';
    	$("#dn1").hide();
    	$("#dn2").hide();
    	$("#dn3").hide();
    	$("#dn4").hide();
    	$("#deliverall").show();
    	$("#deliver").show();
    	$("#deliver1").show();
    	$("#deliver2").hide();
    	$("#hl1").hide();
    	
    	$("#dv1").hide();
    	$("#dv2").hide();
    	$("#dv3").hide();
    	$("#dv4").hide();
    	$("#dv5").show();
    	$("#dv6").show();
    	$("#dv7").show();
    	$("#dv8").show();
    	$("#dhl1").hide();
	}
	else if (document.getElementById("u").value == 'Vodja' || document.getElementById("u").value == 'Administrator' || document.getElementById("u").value == 'Administrator all'){
    	if (document.getElementById("u").value == 'Vodja'){
    		openERP_user = '_vodja';
    	}
    	else if (document.getElementById("u").value == 'Administrator'){
    		openERP_user = 'admin';
    	}
    	else if (document.getElementById("u").value == 'Administrator all'){
    		openERP_user = 'admin';
    		userID = 'mentis';
    	}
    		
    	$("#dn1").show();
    	$("#dn2").show();
    	$("#dn3").show();
    	$("#dn4").show();
    	$("#deliverall").show();
    	$("#deliver").show();
    	$("#deliver1").show();
    	$("#deliver2").hide();
    	$("#hl1").show();
    	
    	$("#dv1").show();
    	$("#dv2").show();
    	$("#dv3").show();
    	$("#dv4").show();
    	$("#dv5").show();
    	$("#dv6").show();
    	$("#dv7").show();
    	$("#dv8").show();
    	$("#dhl1").show();
	}
    	
    instance.session.session_authenticate(
    		document.getElementById("s1").options[so].text,
    		openERP_user,
    		$("#p").attr('value'),
    		false).fail(function(result){alert("Prijava neuspešna");$("#blogin").css('color','black');})
    		.done(function(result){$("#login").attr('class','Closed'); $("#select1").attr('class','Open');fillCat();})        
}
function Exit(){
	instance.session.session_logout();
	$("#p").attr('value','');
	$("#login").attr('class','Open');
	$("#select1").attr('class','Closed');	
}

function fillCat(){
	//Odpri menuje , glede na uporabnika
	user=$("#u").attr('value');	
	if (user=="testo")
		{
		 $("#dn1").click();
		}
	cat.query(['id'])
    .filter([['parent_id','=',34]]).all().then(function(results){    
    for(i=0;i<results.length;i++){ 
        polizdelki.push(results[i].id);    
        }
    })
    cat.query(['id'])
    .filter([['parent_id','=',38]]).all().then(function(results){    
    for(i=0;i<results.length;i++){ 
        izdelki.push(results[i].id);    
        }
    })
}
//Definiraam jQery grid za polnjenje kosar
function initGridBasket(){
	var colm= [{name:'id1', hidden:true}]; 		
	
	if (relacija=='Relacija'){
		groupT=false;
		//colm.push({name:'product_id',width:'400px',sorttype:'text'});		
		colm.push({name:'product_code',width:'100px',sorttype:'text', hidden:false});
		colm.push({name:'product_name',width:'400px',sorttype:'text'});
		colm.push({name:'basket_number',width:'30px',align:'center', hidden:true});			
		colm.push({name:'product_uos_qty',align:'center',sorttype:'number'});
		colm.push({name:'basket_deliverd',align:'center',sorttype:'number'});
		colm.push({name:'partner_id', hidden:true});
		colm.push({name:'qty_delivery_available', hidden:false,sorttype:'number',align:'center'});
	}
	else
	{
		groupT=true;
		//colm.push({name:'product_id',width:'300px',sorttype:'text'});
		colm.push({name:'product_code',width:'100px',sorttype:'text', hidden:true});
		colm.push({name:'product_name',width:'400px',sorttype:'text'});
		colm.push({name:'basket_number',width:'30px',align:'center',sorttype:'number', hidden:false});		
		colm.push({name:'product_uos_qty',align:'center',sorttype:'number'});
		colm.push({name:'basket_deliverd',align:'center',sorttype:'number'});
		colm.push({name:'partner_id', hidden:true});
		colm.push({name:'qty_delivery_available', hidden:false,sorttype:'number',align:'center'});
	}
	groupBY = '';
	if (relacija == 'Relacija 2')
		groupBY = 'product_name';
	else if (relacija == 'Relacija 1')
		groupBY = 'partner_id';
	else
		groupBY = 'product_name';
	
	jQuery("#grid2").jqGrid({
	         datatype: "local",
	         height:'auto',
	         rowNum:'10000',
	         autowidth: true,
 	         colNames:['Id','Šifra', 'Naziv','Koš','Naročena količina','Naloženo','Partner','Prosto'],
 	         colModel:colm,
   	        multiselect: false,            
            viewrecords: true,
            sortname: 'product_name',
            sortorder: "desc",
            grouping:groupT,
            hiddengrid:false,           
            onCellSelect:function(rowid,iCol)
            {                            
            	rId=rowid;
            	cId=iCol;
                if (relacija=='Relacija')
                	iCol=6;
            	switch(iCol){
            	case 3:
            		if ($("#grid2").jqGrid('getCell',rowid,6) != 0)
            			$("#name2").attr('value',$("#grid2").jqGrid('getCell',rowid,6));
            		else
            			$("#name2").attr('value','');
            		$( "#dialog-partner" ).dialog( "open" );
            		break;
            	case 4:
            		if ($("#grid2").jqGrid('getCell',rowid,iCol) != 0)
            			$("#name1").attr('value',$("#grid2").jqGrid('getCell',rowid,iCol));
            		else
            			$("#name1").attr('value','');
            		$( "#dialog-all" ).dialog( "open" );
            		break;
            	case 5:
            		if ($("#grid2").jqGrid('getCell',rowid,iCol) != 0)
            			$("#name").attr('value',$("#grid2").jqGrid('getCell',rowid,iCol));
            		else
            			$("#name").attr('value','');
            		$( "#dialog-partial" ).dialog( "open" );
            		break;           		
            	}
            },
          	groupingView : {
          		groupField : [groupBY],
          		groupColumnShow : [false],
          		groupDataSorted: true,
          		//groupText : ["<b onclick='tClick(this.parentElement);return false;'> {1} - {0}                 </b>"],
          		groupText : ["<b onclick=\"jQuery('#grid2').jqGrid('groupingToggle',this.parentElement.parentElement.id);return false; \">{1} - {0}                 </b>"],
          		groupCollapse : true,
       		    groupOrder: ['asc']        		    
          	},          	
 	         caption: ""
           });             
           $(".ui-jqgrid-titlebar").hide(); 
}
//Polnjene grida za kosare
function osveziGridBasket(event){
	if (basketLocked == 1)
		return;
	basketLocked = 1;
	if (event.data.gotovo){
		$("#kon").css('background-color','#990000');
		$("#run").css('background-color','#000000');
		tStatusValue=['1'];
		sGotovo=true;
	}
	else {
		$("#run").css('background-color','#990000');
		$("#kon").css('background-color','#000000');	
		tStatusValue=['0'];
		sGotovo=false;
	}	
	
	orderBY = '';
	if (relacija == 'Relacija 2')
		orderBY = 'product_id';
	else if (relacija == 'Relacija 1')
		orderBY = 'partner_id';
	else
		orderBY = 'product_id';
	
	if (relacija=='Relacija')
		tStatusValue=['0','1','3'];
	
    $("#grid2").jqGrid("clearGridData"); 
    stock.query(['id','product_id','basket_number','product_uos_qty','basket_deliverd','partner_id','qty_delivery_available'])
    .filter([['type','=','out'],['state','in',['assigned','confirmed']],['location_id','=',12],['basket_status','in',tStatusValue]])
    .order_by(orderBY).all().then(function(moves){		     
    if (moves.length>0)
    	nameT=moves[0].product_id.toString().substring(moves[0].product_id.toString().indexOf(',')+1);
    kolT=0;
    kol1T=0;
    
    for(i=0;i<moves.length;i++){
    	if (moves[i].qty_delivery_available == false)
    		moves[i].qty_delivery_available = 0;
    	
    	product_name = moves[i].product_id.toString().substring(moves[i].product_id.toString().indexOf(',')+1);
    	moves[i].product_id = moves[i].product_id.toString().substring(moves[i].product_id.toString().indexOf(',')+1);
    	
    	product_code = product_name.substring(0,product_name.indexOf(' '));
		product_name = product_name.substring(product_name.indexOf(' ')+1);
		//alert('sifra: '+ product_code + ', naziv: '+ product_name);
		moves[i].partner_id = moves[i].partner_id.toString().substring(moves[i].partner_id.toString().indexOf(',')+1);
		moves[i].product_name = product_name;
		moves[i].product_code = product_code;
    	
    	moves[i].id1=moves[i].id; 
    	if (relacija=='Relacija'){
    		if ((nameT==moves[i].product_id)&&(i+1<moves.length)){
    			kolT+=moves[i].basket_deliverd;
    			kol1T+=moves[i].product_uos_qty;
    			continue;
    		}
    		if (nameT==moves[i].product_id){
    			moves[i].basket_deliverd+=kolT;
    			moves[i].product_uos_qty+=kol1T;
    			if (sGotovo && (kolT >= kol1T))
    				jQuery("#grid2").jqGrid('addRowData',i,moves[i]);
    			if (!sGotovo && (kolT < kol1T))
    				jQuery("#grid2").jqGrid('addRowData',i,moves[i]);
    			kolT=0;
    		}
    		else {
    			moves[i-1].basket_deliverd=kolT;
    			moves[i-1].product_uos_qty=kol1T;
    			if (sGotovo && (kolT >= kol1T))
    				jQuery("#grid2").jqGrid('addRowData',i,moves[i-1]);
    			if (!sGotovo && (kolT < kol1T))
    				jQuery("#grid2").jqGrid('addRowData',i,moves[i-1]);
    			
    			if (i+1==moves.length){
    				if (sGotovo && (kolT >= kol1T))
        				jQuery("#grid2").jqGrid('addRowData',i,moves[i]);
        			if (!sGotovo && (kolT < kol1T))
        				jQuery("#grid2").jqGrid('addRowData',i,moves[i]);
    			}
    				
    			kolT=0;
    		}
    	}
    	else{
    		if (sGotovo)
    			jQuery("#grid2").jqGrid('addRowData',i+1,moves[i]); 
    		else if ((moves[i].qty_delivery_available>0) || userID == 'mentis' || moves[i].basket_deliverd > 0 || relacija == 'Relacija 1') 
    			jQuery("#grid2").jqGrid('addRowData',i+1,moves[i]); 
    	}
    	
    	nameT=moves[i].product_id;
    	kolT=moves[i].basket_deliverd;
    	kol1T=moves[i].product_uos_qty;
    }
    
    if (relacija=='Relacija')
    	$("#grid2").jqGrid('sortGrid','qty_delivery_available',true,'desc');
    else
    	$("#grid2").jqGrid('sortGrid','basket_number',true,'asc');
    basketLocked = 0;
    });	
}

//Definiram jqery grid za delovne naloge
function initGridDn1()
{
	var colm=[{name:'id1', hidden:true}];
	colm.push({name:'product_code',width:'130px',sorttype:'text'});
	colm.push({name:'product_name',width:'970px',sorttype:'text'});	
	colm.push({name:'product_qty',align:'center',sorttype:'number'}); //naroceno
	
	if (vrstaIzdelka=='Polizdelki_testo' || vrstaIzdelka=='Hladilnica' || vrstaIzdelka=='Dodelava')
		colm.push({name:'product_qty_onstock',align:'center',sorttype:'number'}); //na zalogi
	
	if (vrstaIzdelka=='Polizdelki_testo' || vrstaIzdelka == 'Polizdelki')
		colm.push({name:'product_on_bom_qty_ready',align:'center',sorttype:'number'});
	
	
	if (vrstaIzdelka!='Hladilnica'){
		colm.push({name:'product_delo',align:'center',sorttype:'number'});
		colm.push({name:'produced',align:'center',sorttype:'number'});
	}
	
	if (vrstaIzdelka == 'Polizdelki_testo' || vrstaIzdelka == 'Polizdelki' || vrstaIzdelka == 'Hladilnica')
		colm.push({name:'scrap',align:'center',sorttype:'number', hidden:true});
	else
		colm.push({name:'scrap',align:'center',sorttype:'number'});
	
	if (vrstaIzdelka=='Izdelki' || vrstaIzdelka=='Dodelava' || vrstaIzdelka == 'Polizdelki'){
		colm.push({name:'produced_stock',align:'center',sorttype:'number'});
	}
	else {
		colm.push({name:'produced_stock',align:'center',hidden:true});
	}
	colm.push({name:'product_with_bom_name',align:'center',sorttype:'text', hidden:true});
	
	if (vrstaIzdelka=='Hladilnica')
		colm.push({name:'product_on_bom_qty_ready',align:'center',sorttype:'number'});
	
	colm.push({name:'created_from_op',align:'center',hidden:true});
	
	if (vrstaIzdelka=='Polizdelki_testo')
		useGrouping = true;
	else
		useGrouping = false; 
	
	var coln=['Id','Sifra','Naziv','Nar.','Nalož.','Na volj.','Izdel.','Odpis','Hlad.','Testo','fromOP'];
	if (vrstaIzdelka=='Polizdelki_testo')
		var coln=['Id','Sifra','Naziv','Nar.','Zaloga','Nalož.','Za izd.','Izdel.','Odpis','Hlad','Testo','fromOP'];
	if (vrstaIzdelka=='Izdelki')
		var coln=['Id','Sifra','Naziv','Nar.','Na volj.','Izdel.','Odpis','Hlad.','Testo','fromOP'];
	if (vrstaIzdelka=='Dodelava')
		var coln=['Id','Sifra','Naziv','Nar.','Zaloga','Na volj.','Izdel.','Odpis','Hlad.','Testo','fromOP'];
	if (vrstaIzdelka=='Hladilnica')
		var coln=['Id','Sifra','Naziv','Nar.','Zaloga','Odpis','Hlad','Testo','Naloženo','fromOP'];
	
	jQuery("#grid1").jqGrid({
		datatype: "local",
	    height:'auto',
	    rowNum:'10000',
	    autowidth: true,
	    colNames:coln,	        
 	    colModel:colm,
   	    multiselect: false,            
        viewrecords: true,
        sortname: 'product_name',
        sortorder: "asc",
        grouping:useGrouping,
        hiddengrid:false,           
        onCellSelect:function(rowid,iCol){
        	rId=rowid;
            cId=iCol;
              	
            switch(vrstaIzdelka){
            	case 'Polizdelki_testo':
            		$("#testo_izdelano").attr('value', '');
            		$("#lbl_testo_izdelano").text("Testo izdelano (" + $("#grid1").jqGrid('getCell',rowid,7) + "):");
            		
            	    $("#dialog-testo").dialog('option','title',$("#grid1").jqGrid('getCell',rowid,2));
            		$( "#dialog-testo" ).dialog( "open" );
            		break;
            	case 'Hladilnica':
            		$("#hladilnica_izdelano").attr('value', '');
            		$("#lbl_hladilnica_izdelano").text("Naloženo (" + $("#grid1").jqGrid('getCell',rowid,8) + "):");
            		
            	    $("#dialog-hladilnica").dialog('option','title',$("#grid1").jqGrid('getCell',rowid,2));
            		$( "#dialog-hladilnica" ).dialog( "open" );
            		break;	
              	case 'Polizdelki':
//              		if ($("#grid1").jqGrid('getCell',rowid,4) != 0)
//              			$("#polizdelki_izdelano").attr('value',$("#grid1").jqGrid('getCell',rowid,4));
//              		else
              			$("#polizdelki_izdelano").attr('value', '');
              		$("#lbl_polizdelki_izdelano").text("Osnova izdelano (" + $("#grid1").jqGrid('getCell',rowid,6) + "):");
              		
              		if ($("#grid1").jqGrid('getCell',rowid,7) != 0)
              			$("#polizdelki_stock").attr('value',$("#grid1").jqGrid('getCell',rowid,7));
              		else
              			$("#polizdelki_stock").attr('value', '');
            	    $( "#dialog-polizdelki" ).dialog('option','title',$("#grid1").jqGrid('getCell',rowid,2));
            	    $( "#dialog-polizdelki" ).dialog( "open" );
            		break;
            		
              	case 'Izdelki':
//              		if ($("#grid1").jqGrid('getCell',rowid,4) != 0)
//              			$("#izdelki_izdelano").attr('value',$("#grid1").jqGrid('getCell',rowid,4));
//              		else
              			$("#izdelki_izdelano").attr('value', '');
              		$("#lbl_izdelki_izdelano").text("Izdelki izdelano (" + $("#grid1").jqGrid('getCell',rowid,5) + "):");
              			
              		if ($("#grid1").jqGrid('getCell',rowid,6) != 0)
              			$("#izdelki_odpis").attr('value',$("#grid1").jqGrid('getCell',rowid,6));
              		else
              			$("#izdelki_odpis").attr('value', '');
              		if ($("#grid1").jqGrid('getCell',rowid,7) != 0)
              			$("#izdelki_stock").attr('value',$("#grid1").jqGrid('getCell',rowid,7));
              		else
              			$("#izdelki_stock").attr('value', '');
            	    $( "#dialog-izdelki" ).dialog('option','title',$("#grid1").jqGrid('getCell',rowid,2));
            	    $( "#dialog-izdelki" ).dialog( "open" );
            		break;		
              	
	            case 'Dodelava':
//	            	if ($("#grid1").jqGrid('getCell',rowid,4) != 0)
//              			$("#izdelki_izdelano").attr('value',$("#grid1").jqGrid('getCell',rowid,4));
//              		else
              			$("#izdelki_izdelano").attr('value', '');
              		$("#lbl_izdelki_izdelano").text("Izdelki izdelano (" + $("#grid1").jqGrid('getCell',rowid,6) + "):");
              		
              		if ($("#grid1").jqGrid('getCell',rowid,7) != 0)
              			$("#izdelki_odpis").attr('value',$("#grid1").jqGrid('getCell',rowid,7));
              		else
              			$("#izdelki_odpis").attr('value', '');
              		if ($("#grid1").jqGrid('getCell',rowid,8) != 0)
              			$("#izdelki_stock").attr('value',$("#grid1").jqGrid('getCell',rowid,8));
              		else
              			$("#izdelki_stock").attr('value', '');
	        	    $( "#dialog-izdelki" ).dialog('option','title',$("#grid1").jqGrid('getCell',rowid,2));
	        	    $( "#dialog-izdelki" ).dialog( "open" );
	        		break;		
	        }
        },
        groupingView:{
        	groupField : ['product_with_bom_name'],
          	groupColumnShow : [false],
          		//groupText : ["<b onclick='tClick(this.parentElement);return false;'> {1} - {0}                                         </b>"],
          	groupText : ["<b onclick=\"jQuery('#grid1').jqGrid('groupingToggle',this.parentElement.parentElement.id);return false; \">{1} - {0}                 </b>"],
          	groupCollapse : true,
       		groupOrder: ['asc']        		    
        },
        caption: ""
	});             
}

//Polnjene grida za delovne naloge
function osveziGridDn1(event){
	if (basketLocked == 1)
		return;
	basketLocked = 1;
	
	if (event.data.gotovo){
		$("#konDn1").css('background-color','#990000');
		$("#runDn1").css('background-color','#000000');
		tStatusValue=['1'];
		sGotovo=true;
	}
	else {
		$("#runDn1").css('background-color','#990000');
		$("#konDn1").css('background-color','#000000');	
		tStatusValue=['0'];
		sGotovo=false;
	}
    $("#grid1").jqGrid("clearGridData");     
    if (vrstaIzdelka=='Polizdelki_testo')
    	tStatus='status_testo';
    else
    	tStatus='status_izdelki';
    
    dressingT = ['false'];
    if (vrstaIzdelka=='Dodelava')
    	dressingT = ['true'];
    else if (vrstaIzdelka=='Hladilnica'){
    	dressingT = ['true', 'false'];
    	tStatusValue=['0','1'];
    }
    
        mrp.query(['id','product_id','product_qty','produced','scrap','produced_phantom','scrap_phantom','produced_stock',
               'product_on_bom_qty_available','product_on_bom_qty_stock','product_with_bom_name','product_on_bom_qty_ready',
               'product_qty_onstock','created_from_op','product_on_bom_qty_P_ready','product_is_product','product_on_bom_qty_O_ready','product_qty_ordered'])
    	.filter([['product_cat','in',kategorije],[tStatus,'in',tStatusValue],['dressing','in',dressingT],['state','in',['ready','in_production','confirmed']]])
    	.order_by('product_with_bom_name').all().then(function(results){
    		         
    		for(i=0;i<results.length;i++){
    			
    			product_name = results[i].product_id.toString().substring(results[i].product_id.toString().indexOf(',')+1);

    			if (vrstaIzdelka=='Hladilnica' && results[i].product_is_product != ''){
    				//results[i].product_name = results[i].product_with_bom_name;
      				//results[i].product_code = '';
    				results[i].product_qty_onstock=results[i].product_on_bom_qty_stock;
      				results[i].product_on_bom_qty_ready = results[i].product_on_bom_qty_O_ready;
      				//product_name = results[i].product_is_product;
      				
      				//alert(results[i].product_is_product);
      				product_name = results[i].product_is_product.toString().substring(results[i].product_is_product.toString().indexOf(',')+1)+'~';
      			}
    			
    			product_code = product_name.substring(0,product_name.indexOf(' '));
    			product_name = product_name.substring(product_name.indexOf(' ')+1);
    			
    			results[i].product_name = product_name;
    			results[i].product_code = product_code;
    			
    			
    			//Odstejemo nalozeno kolicino
    			//alert(product_name);
    			//alert(results[i].product_qty_onstock);
    			//alert(results[i].product_on_bom_qty_ready);
    			//alert(results[i].product_on_bom_qty_O_ready);
    			
        		results[i].product_qty_onstock = results[i].product_qty_onstock - results[i].product_on_bom_qty_ready
    			
    			if (vrstaIzdelka=='Polizdelki_testo'){
    				results[i].produced=results[i].produced_phantom;
    				results[i].scrap=results[i].scrap_phantom;
    				results[i].product_delo=(results[i].product_qty - results[i].produced_phantom + results[i].scrap_phantom 
    						- results[i].product_on_bom_qty_ready -results[i].product_on_bom_qty_P_ready);
    				if (results[i].product_on_bom_qty_P_ready>0)
    					results[i].product_on_bom_qty_ready = results[i].product_on_bom_qty_ready + '('+results[i].product_on_bom_qty_P_ready+')'
    			}
    			if (vrstaIzdelka=='Polizdelki'){
    				results[i].product_delo=(results[i].produced_phantom-results[i].scrap_phantom-results[i].produced);
    			}
    			if (vrstaIzdelka=='Izdelki'||vrstaIzdelka=='Dodelava'){
    				results[i].product_delo=results[i].product_on_bom_qty_available;
    			}
    			if (vrstaIzdelka=='Hladilnica'){
    				//results[i].product_qty = results[i].product_qty - results[i].product_qty_ordered;
    				//alert(results[i].product_qty + ' -- ' + results[i].product_qty_ordered);
    				if (results[i].product_qty != results[i].product_qty_ordered)
    					results[i].product_qty = results[i].product_qty - results[i].product_qty_ordered;
    				
    				//old results[i].product_delo = results[i].product_qty;
    				
    				
    				//old_old results[i].product_delo=results[i].product_qty_onstock;
    			}
    			
    			results[i].id1=results[i].id;
    			
    			//Ce je narocilo iz OP
    			if (results[i].created_from_op == true)
    				if (vrstaIzdelka=='Izdelki'||vrstaIzdelka=='Dodelava')
    					results[i].product_qty = '0('+results[i].product_qty+')';
    				else
    					results[i].product_qty = 0;
    				
    			if (vrstaIzdelka=='Polizdelki_testo'){
    				iDelo = parseInt(results[i].product_delo);
    				if (iDelo < 0) //if (sGotovo && (iDelo < 0))
    					results[i].product_delo = '0';
    				jQuery("#grid1").jqGrid('addRowData',i+1,results[i]);  
    			}
    			if (vrstaIzdelka=='Polizdelki'){
    				iDelo = parseInt(results[i].product_delo); //negativne vrednosti ne pokazemo (ce smo naredili vec polizdelkov kot testa)
    				if (iDelo < 0)
    					results[i].product_delo = '0';
    				
    				if (results[i].product_delo!='0' || userID == 'mentis' || sGotovo || results[i].produced>0)
    					jQuery("#grid1").jqGrid('addRowData',i+1,results[i]);
    			}   
    			if (vrstaIzdelka=='Izdelki'||vrstaIzdelka=='Dodelava'){
    				if (results[i].product_delo!='0' || userID == 'mentis' || sGotovo || results[i].produced>0 || vrstaIzdelka=='Dodelava') 
    					jQuery("#grid1").jqGrid('addRowData',i+1,results[i]); 
    			}
    			if (vrstaIzdelka=='Hladilnica'){
    				if ((results[i].product_qty>'0' && (results[i].product_qty_onstock>'0' || results[i].product_on_bom_qty_ready>0)) || userID == 'mentis' || vrstaIzdelka=='Dodelava') 
    					jQuery("#grid1").jqGrid('addRowData',i+1,results[i]); 
    			}
    		}
    	$("#grid1").jqGrid('sortGrid','product_with_bom_name',true,'asc');
    	//$("#formDN").prop("disabled", false);
    	//$("#formDN").removeAttr("disabled");
    	basketLocked = 0;
     });
    
}
/////////////////////////////////////////////////////////////////////////

function testoFill(tip){
	$( "#dialog-testo" ).dialog("close");
	id1=$("#grid1").jqGrid('getCell',rId,0);
	id1=parseInt(id1);
	
	kol = validateInput( $("#testo_izdelano").attr('value') );
	if (kol == 'err')
		return;
	
	kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
	kol_vdelu = parseInt($("#grid1").jqGrid('getCell',rId,6));
	kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,7));
	kol_skupaj = kol+kol_izdelana;
	
	if (tip=="close"){
		if (kol_skupaj < kol_narocena){
			$("#label_value_warning").text("Vnesli ste količino, ki je MANJŠA od naročene, nadaljujem?");
			$("#dialog-value-warning")
				.data('parent', 'fillTesto')
				.dialog("open");
		}
		else{
			mrp.call('set_testo_produced',[id1,kol_skupaj,0,1]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else
					refreshRow(tip,'grid1',true,true,false,false,kol_skupaj,0,0,0);
			});
		}
	}
	else {
		mrp.call('set_testo_produced',[id1,kol_skupaj,0,0]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow(tip,'grid1',true,true,false,false,kol_skupaj,0,0,0);
		});
	}
}
function hladilnicaFill(tip){
	$( "#dialog-hladilnica" ).dialog("close");
	id1=$("#grid1").jqGrid('getCell',rId,0);
	id1=parseInt(id1);
	
	kol = validateInput( $("#hladilnica_izdelano").attr('value') );
	if (kol == 'err')
		return;
	
	kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
	kol_vdelu = parseInt($("#grid1").jqGrid('getCell',rId,4));
	kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,8));
	kol_skupaj = kol+kol_izdelana;
	
	//alert(kol+', '+kol_vdelu+', '+kol_izdelana+', '+kol_skupaj);
	if ((kol_vdelu-kol) < 0){
		$("#label_general_warning").text("Ne morete naložiti več izdelkov kot jih je na voljo v hladilnici!");
		$("#dialog-general-warning").dialog("option", "height", 260);
		$("#dialog-general-warning").dialog("open");
		return;
	}
	
	if (tip=="close"){
		if (kol_skupaj < kol_narocena){
			$("#label_value_warning").text("Vnesli ste količino, ki je MANJŠA od naročene, nadaljujem?");
			$("#dialog-value-warning")
				.data('parent', 'fillHladilnica')
				.dialog("open");
		}
		else{
			mrp.call('set_hladilnica_produced',[id1,kol_skupaj,1]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else
					refreshRow_new(tip,'grid1',false,false,false,false,false,true,true,0,0,0,0,0,kol_skupaj,(kol_vdelu-kol));
			});
		}
	}
	else {
		mrp.call('set_hladilnica_produced',[id1,kol_skupaj,0]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow_new(tip,'grid1',false,false,false,false,false,true,true,0,0,0,0,0,kol_skupaj,(kol_vdelu-kol));
		});
	}
}
function polizdelkiFill(tip){
	$( "#dialog-polizdelki" ).dialog("close");
	id1=$("#grid1").jqGrid('getCell',rId,0);
	id1=parseInt(id1);
	
	kol = validateInput( $("#polizdelki_izdelano").attr('value') );
	kol1 = validateInput( $("#polizdelki_stock").attr('value') );
	if (kol == 'err' || kol1 == 'err')
		return;
	
	kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
	kol_vdelu = parseInt($("#grid1").jqGrid('getCell',rId,5));
	kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,6));
	kol_skupaj = kol+kol_izdelana;
	from_OP = $("#grid1").jqGrid('getCell',rId,10);
	//alert(kol_narocena+','+kol_123+''+kol+', '+kol_vdelu+', '+kol_izdelana+', '+kol_skupaj);
	//alert('From OP:' + from_OP);
	
	if (tip=="close"){
		if (kol_skupaj < kol_narocena){
			$("#label_value_warning").text("Vnesli ste količino, ki je MANJŠA od naročene, nadaljujem?");
			$("#dialog-value-warning")
				.data('parent', 'fillPolIzdelek')
				.dialog("open");
		}
		else{
			mrp.call('set_izdelek_produced',[id1,kol_skupaj,kol1,1]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else
					refreshRow(tip,'grid1',true,false,true,false,kol_skupaj,0,kol1,0);
			});
		}	
	}
	else{
		mrp.call('set_izdelek_produced',[id1,kol_skupaj,kol1,0]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow(tip,'grid1',true,false,true,false,kol_skupaj,0,kol1,0);
		});
	}
}

function izdelkiFill(tip){
	var i1,i2;
	$( "#dialog-izdelki" ).dialog("close");
	id1=$("#grid1").jqGrid('getCell',rId,0);
	id1=parseInt(id1);
	
	kol = validateInput( $("#izdelki_izdelano").attr('value') );
	kol1 = validateInput( $("#izdelki_odpis").attr('value') );
	kol2 = validateInput( $("#izdelki_stock").attr('value') );
	if (kol == 'err' || kol1 == 'err' || kol2 == 'err')
		return;
	
	if (vrstaIzdelka=='Dodelava'){
		kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
		kol_vdelu = parseInt($("#grid1").jqGrid('getCell',rId,5));
		kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,6));
		kol_skupaj = kol+kol_izdelana;
		from_OP = $("#grid1").jqGrid('getCell',rId,10);
	}
	else{
		kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
		kol_vdelu = parseInt($("#grid1").jqGrid('getCell',rId,4));
		kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,5));
		kol_skupaj = kol+kol_izdelana;
		from_OP = $("#grid1").jqGrid('getCell',rId,9);
	}
	//alert(kol+', '+kol1+', '+kol2+', '+kol_narocena+', '+kol_vdelu+', '+kol_izdelana+', '+kol_skupaj);
	//alert(from_OP);
	
	if (kol1+kol2 > kol_skupaj){
		$("#label_general_warning").text("Odpisa in izdelkov v hladilnici ne more biti več kot ste jih spekli!");
		$("#dialog-general-warning").dialog("option", "height", 260);
		$("#dialog-general-warning").dialog("open");
		return;
	}
	
	tipZakljucka = tip
	if (from_OP == 'true' && kol2 == 0){
		$("#label_value_warning").text("Izdelek je naročen na zalogo. Če ni namenjen nadaljni dodelavi ga premaknite v hladilico. Nadaljujem?");
		$("#dialog-value-warning")
			.data('parent', 'fillIzdelek')
			.dialog("option", "height", 320)
			.dialog("open");
		//.dialog("option", "height", 310);
		//$("#dialog-general-warning").dialog("open");
		return;
	}
	if (tip=="close"){
//		if ((kol_vdelu-kol > 0) && (vrstaIzdelka == "Izdelki")){
//			$("#label_general_warning").text("Pri zaključevanju morate speči celotno količino, ki je na voljo!");
//			$("#dialog-general-warning").dialog("option", "height", 260);
//			$("#dialog-general-warning").dialog("open");
//			return;
//		}
		if (kol_skupaj < kol_narocena){
			$("#label_value_warning").text("Vnesli ste količino, ki je MANJŠA od naročene, nadaljujem?");
			$("#dialog-value-warning")
				.data('parent', 'fillIzdelek')
				.dialog("open");
		}
		else{
			mrp.call('set_izdelek_produced1',[id1,kol_skupaj,kol1,kol2,1,vrstaIzdelka]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else if (result == 'must_not_consume_all'){
					$("#label_general_warning").text("Pri zaključevanju ne morete porabiti celotno količino, ki je na voljo, ker obstajajo še drugi izdelki z enako osnovo!");
					$("#dialog-general-warning").dialog("option", "height", 320);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == 'must_not_move'){
					$("#label_general_warning").text("Izdelka ne morete premakniti nazaj v delo. Najprej povečajte razpoložljivo količino!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == 'not_all_consumed'){
					$("#label_general_warning").text("Pri zaključevanju morate speči celotno količino, ki je na voljo!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == 'not_available'){
					$("#label_general_warning").text("Ne morete speči več izdelkov kot je pripravljene osnove!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == false){
					$("#label_general_warning").text("Ne morete izdelati manjšo količino izdelkov, ker so nekateri že v košarah!");
					$("#dialog-general-warning").dialog("option", "height", 300);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else
					refreshRow_new(tip,'grid1',true,true,true,false,true,false,false,kol_skupaj,kol1,kol2,0,(kol_vdelu-kol),0,0);
			});
		}
	}
	else {
		mrp.call('set_izdelek_produced1',[id1,kol_skupaj,kol1,kol2,0,vrstaIzdelka]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else if (result == 'not_available'){
				$("#label_general_warning").text("Ne morete speči več izdelkov kot je pripravljene osnove!");
				$("#dialog-general-warning").dialog("option", "height", 260);
				$("#dialog-general-warning").dialog("open");
				return;
			}
			else if (result == false){
				$("#label_general_warning").text("Ne morete izdelati manjšo količino izdelkov, ker so nekateri že v košarah!");
				$("#dialog-general-warning").dialog("option", "height", 300);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow_new(tip,'grid1',true,true,true,false,true,false,false,kol_skupaj,kol1,kol2,0,(kol_vdelu-kol),0,0);
		});
	}
}


function basketFillPartial(tip){
	$( "#dialog-partial" ).dialog("close");
	id1=$("#grid2").jqGrid('getCell',rId,0);
	id1=parseInt(id1);
	
	kol = validateInput( $("#name").attr('value') );
	if (kol == 'err')
		return;
	kol_grid=parseInt($("#grid2").jqGrid('getCell',rId,4));
	
	if (tip=="close"){
		if (kol < kol_grid){
			$("#label_value_warning").text("Vnesli ste količino, ki je MANJŠA od naročene, nadaljujem?");
			$("#dialog-value-warning")
				.data('parent', 'fillPartial')
				.dialog("open");
		}
		else if (kol > kol_grid){
			$("#label_value_warning").text("Vnesli ste količino, ki je VEČJA od naročene, nadaljujem?");
			$("#dialog-value-warning")
				.data('parent', 'fillPartial')
				.dialog("open");
		}
		else{
			stock.call('set_basket_deliverd',[id1,kol,1]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else if (result == false){
					$("#label_general_warning").text("Na voljo imate manjšo količino kot ste jo vnesli!");
					$("#dialog-general-warning").dialog("open");
				}
				else
					refreshRow(tip,'grid2',false,false,false,true,0,0,0,kol);
			});
		}
	}
	else{
		stock.call('set_basket_deliverd',[id1,kol,0]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else if (result == false){
				$("#label_general_warning").text("Na voljo imate manjšo količino kot ste jo vnesli!");
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow(tip,'grid2',false,false,false,true,0,0,0,kol);
		});
	}
}

function basketFillAll(){
	id1=$("#grid2").jqGrid('getCell',rId,0);
	id1=parseInt(id1);
	kol=$("#grid2").jqGrid('getCell',rId,4);
	
	stock.call('set_basket_deliverd',[id1,kol,1]).then(function(result){
		if (result == 'stock_moved'){
			$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
			$("#dialog-general-warning").dialog("option", "height", 280);
			$("#dialog-general-warning").dialog("open");
		}
		else if (result == false){
			$("#label_general_warning").text("Na voljo imate manjšo količino kot ste jo vnesli!");
			$("#dialog-general-warning").dialog("open");
		}
		else
			refreshRow('close','grid2',false,false,false,true,0,0,0,kol);
	});
}

function validateInput(input){
	if (input && input.charAt(0) == '0'){
		input = input.substring(1);
	}
		
	if (input == '')
		input = 0;
		
	if (!$.isNumeric(input)){
		$("#label_general_warning").text("Vnesli ste alfanumerične znake!");
		$("#dialog-general-warning").dialog("option", "height", 220);
		$("#dialog-general-warning").dialog("open");
		return 'err';
	}
//	if (input < 0){
//		$("#label_general_warning").text("Vnesli ste negativno število!");
//		$("#dialog-general-warning").dialog("option", "height", 220);
//		$("#dialog-general-warning").dialog("open");
//		return 'err';
//	}
	return parseInt(input);
}

//Uporabnik potrdil, da je vnesel manjso kolicino kot je narocena
function updateDBValues(arg){
	$("#dialog-value-warning").dialog("close");
	//alert('updateDBValues: ' + arg)
	
	if (arg == 'fillPartial'){
		id1=$("#grid2").jqGrid('getCell',rId,0);
		id1=parseInt(id1);
		
		kol=$("#name").attr('value');
		kol_grid=$("#grid2").jqGrid('getCell',rId,4);
		
		stock.call('set_basket_deliverd',[id1,kol,1]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else if (result == false){
				$("#label_general_warning").text("Na voljo imate manjšo količino kot ste jo vnesli!");
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow('close','grid2',false,false,false,true,0,0,0,kol);
		});
	}
	else if (arg == 'fillTesto'){
		id1=$("#grid1").jqGrid('getCell',rId,0);
		id1=parseInt(id1);
		
		kol = validateInput( $("#testo_izdelano").attr('value') );
		
		kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
		kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,7));
		kol_skupaj = kol+kol_izdelana;
		
		mrp.call('set_testo_produced',[id1,kol_skupaj,0,1]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow('close','grid1',true,true,false,false,kol_skupaj,0,0,0);
		});
	}
	else if (arg == 'fillHladilnica'){
		id1=$("#grid1").jqGrid('getCell',rId,0);
		id1=parseInt(id1);
		
		kol = validateInput( $("#hladilnica_izdelano").attr('value') );
		
		kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
		kol_vdelu = parseInt($("#grid1").jqGrid('getCell',rId,4));
		kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,8));
		kol_skupaj = kol+kol_izdelana;
		
		mrp.call('set_hladilnica_produced',[id1,kol_skupaj,1]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow_new('open','grid1',false,false,false,false,false,true,true,0,0,0,0,0,kol_skupaj,(kol_vdelu-kol));
		});
	}
	else if (arg == 'fillPolIzdelek'){
		id1=$("#grid1").jqGrid('getCell',rId,0);
		id1=parseInt(id1);
		
		kol = validateInput( $("#polizdelki_izdelano").attr('value') );
		kol1 = validateInput( $("#polizdelki_stock").attr('value') );
		
		kol_narocena = parseInt($("#grid1").jqGrid('getCell',rId,3));
		kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,6));
		kol_skupaj = kol+kol_izdelana;
		
		mrp.call('set_izdelek_produced',[id1,kol_skupaj,kol1,1]).then(function(result){
			if (result == 'stock_moved'){
				$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
				$("#dialog-general-warning").dialog("option", "height", 280);
				$("#dialog-general-warning").dialog("open");
			}
			else
				refreshRow('close','grid1',true,false,true,false,kol_skupaj,0,kol1,0);
		});
	}
	else if (arg == 'fillIzdelek'){
		id1=$("#grid1").jqGrid('getCell',rId,0);
		id1=parseInt(id1);
		
		kol = validateInput( $("#izdelki_izdelano").attr('value') );
		kol1 = validateInput( $("#izdelki_odpis").attr('value') );
		kol2 = validateInput( $("#izdelki_stock").attr('value') );
		
		if (vrstaIzdelka=='Dodelava')
			kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,6));
		else
			kol_izdelana = parseInt($("#grid1").jqGrid('getCell',rId,5));
		kol_skupaj = kol+kol_izdelana;
		
		if (tipZakljucka == 'close')
		{
			mrp.call('set_izdelek_produced1',[id1,kol_skupaj,kol1,kol2,1,vrstaIzdelka]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else if (result == 'must_not_consume_all'){
					$("#label_general_warning").text("Pri zaključevanju ne morete porabiti celotno količino, ki je na voljo, ker obstajajo še drugi izdelki z enako osnovo!");
					$("#dialog-general-warning").dialog("option", "height", 320);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == 'must_not_move'){
					$("#label_general_warning").text("Izdelka ne morete premakniti nazaj v delo. Najprej povečajte razpoložljivo količino!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == 'not_all_consumed'){
					$("#label_general_warning").text("Pri zaključevanju morate speči celotno količino, ki je na voljo!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == 'not_available'){
					$("#label_general_warning").text("Ne morete speči več izdelkov kot je pripravljene osnove!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == false){
					$("#label_general_warning").text("Ne morete izdelati manjšo količino izdelkov, ker so nekateri že v košarah!");
					$("#dialog-general-warning").dialog("option", "height", 300);
					$("#dialog-general-warning").dialog("open");
				}
				else
					refreshRow('close','grid1',true,true,true,false,kol_skupaj,kol1,kol2,0);
			});
		}
		else {
			mrp.call('set_izdelek_produced1',[id1,kol_skupaj,kol1,kol2,0,vrstaIzdelka]).then(function(result){
				if (result == 'stock_moved'){
					$("#label_general_warning").text("Trenutno se izvaja lansiranje proizvodnje. Prosim počakajte nekaj minut.");
					$("#dialog-general-warning").dialog("option", "height", 280);
					$("#dialog-general-warning").dialog("open");
				}
				else if (result == 'not_available'){
					$("#label_general_warning").text("Ne morete speči več izdelkov kot je pripravljene osnove!");
					$("#dialog-general-warning").dialog("option", "height", 260);
					$("#dialog-general-warning").dialog("open");
					return;
				}
				else if (result == false){
					$("#label_general_warning").text("Ne morete izdelati manjšo količino izdelkov, ker so nekateri že v košarah!");
					$("#dialog-general-warning").dialog("option", "height", 300);
					$("#dialog-general-warning").dialog("open");
				}
				else
					refreshRow_new(tipZakljucka,'grid1',true,true,true,false,true,false,false,kol_skupaj,kol1,kol2,0,(kol_vdelu-kol),0,0);
			});
		}
	}
}

function refreshRow(tip, grid, k, k1, k2, k3, kol, kol1, kol2, kol3){
	if ((sGotovo&&tip=="close")||(!sGotovo&&tip=="open")){
		rowData = $('#'+grid).jqGrid('getRowData', rId);    		
        if (k) rowData.produced=kol;
    	if (k1) rowData.scrap=kol1;
    	if (k2) rowData.produced_stock=kol2;
    	if (k3) rowData.basket_deliverd=kol3;
    	$('#'+grid).jqGrid('setRowData', rId, rowData);
    }
    else{
    	$('#'+grid).jqGrid('delRowData',rId);
    	//hideGroup(grid, rId);
    }  
}

function refreshRow_new(tip, grid, k, k1, k2, k3, k4, k5, k6, kol, kol1, kol2, kol3, kol4, kol5, kol6){
	if ((sGotovo&&tip=="close")||(!sGotovo&&tip=="open")){
		rowData = $('#'+grid).jqGrid('getRowData', rId);    		
        if (k) rowData.produced=kol;
    	if (k1) rowData.scrap=kol1;
    	if (k2) rowData.produced_stock=kol2;
    	if (k3) rowData.basket_deliverd=kol3;
    	if (k4) rowData.product_delo=kol4;
    	if (k5) rowData.product_on_bom_qty_ready=kol5;
    	if (k6) rowData.product_qty_onstock=kol6;
    	$('#'+grid).jqGrid('setRowData', rId, rowData);
    }
    else{
    	$('#'+grid).jqGrid('delRowData',rId);
    	//hideGroup(grid, rId);
    }  
}

//skrij group header basket deliver če ni več postavk / ne dela !!!!
function hideGroup(grid, rId) {
	alert('Grid: ' + grid + ', row: ' + rId);
    var i, groups = $('#'+grid).jqGrid("getGridParam", "groupingView").groups;
    if(groups){   
    	l = groups.length;
        idSelectorPrefix = "#" + grid + "ghead_0_";
        for (i = 0; i < l; i++) {
        	alert(groups[i].cnt);
        	alert('Group id: + ' + groups[i].id);	
        	for (j=0; j<groups[i].cnt; j++){
        		alert('Row v grupu:' + groups[i][j]);
        	}
        	
        	if (groups[i].cnt == 0) {
        		// hide the grouping row
        		alert('bi morali skriti: ' + idSelectorPrefix + i);
        		$(idSelectorPrefix + i).hide();
        	}
        }
    }
}

////////////////
//Izhod iz posameznega menuja na glavni meni
function izhod(event){
	if (basketLocked == 1)
		return;
	$("#"+event.data.divID).attr('class','Closed');
	$("#select1").attr('class','Open');		
}
