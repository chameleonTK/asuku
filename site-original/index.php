<html>
	<head>
		<meta http-equiv="Content-Language" content="th"> 
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<title> Simsimi ?? </title>
		<link rel="stylesheet" href="css/bootstrap.css">
		<link rel="stylesheet" href="css/style.css">
		<link rel="icon" type="image/png" href="img/favicon.png" />
		<script src="js/jquery.min.js"></script>
		<script src="js/bootstrap.min.js"></script>
		<script src="js/sonic.js"></script>
		<script src="js/mysonic.js"></script>
		<script type="text/javascript" src="js/jquery-ui.js"></script>
		<script>
			$(function(){

				function enterKey(){
					alert("hello");
				}


				function answer_chat(data,type){
					var chatbox = document.getElementById("chat");
					var rand_id = Math.floor(Math.random()*10000)%5000;
					$("#chatbox").append('<li class="'+type+'"> <div class="image circle"></div> <p id="'+rand_id+'" class="chat-msg">'+data+'</p> </li>');
					chatbox.scrollTop = chatbox.scrollHeight;
					return rand_id
				}

				function sendQuestion(){
					var qst = $("#qst").val();
					qst = qst.replace(/[\n\r\t]/g, ""); 
					qst = $.trim(qst);

					if(qst == '') return;

					console.log(qst);

									
					answer_chat(qst,"me")
					var id;

					$.ajax("client.php", { data:{question:qst},
					    type: "POST",
					    beforeSend: function() {
					        //$("#load").fadeIn();
					        id = answer_chat("","you");
					      	var element = $("#"+id);
					      	console.log(id);
					        sonicstart(element);

					    },
					    error: function() {
					        //$("#load").animate({backgroundColor:"red"},'fast').delay(500).fadeOut();
					        //$("#load").animate({backgroundColor:"black"},'fast');
					    },
					    success: function(data) {
					    	
						    //$("#load").animate({backgroundColor:"green"},'fast').delay(500).fadeOut();
						    var wait_sec = Math.floor(Math.random()*10000)%3000;
							setTimeout(function(){
								var last_msg = $("#"+id);
								last_msg.html(data);
							}, wait_sec);
					       //$("#load").animate({backgroundColor:"black"},'fast');
					    }
					});

					// clean up text box
					$('#qst').val('')
				}


				$("#send").click(sendQuestion);

				$('#qst').keyup(function(e){
				    if(e.keyCode == 13){ sendQuestion(); }
				});

			});
		</script>
	</head>
	<body>
		<div id="in"></div>

		<div id="content" style="padding: 20px;">

			<div id="chat" style="height:80%;overflow: hidden;"> 
				<ul class="ans" id="chatbox">
				</ul>

			</div>

			<div style="height:50px;text-align: center;">
			    <input type="text" class="form-control" id="qst">
			    <button id="send" type="button" class="btn btn-default btn-lg"> Enter </button>
			</div>
			
		</div>
	</body>
</html>
