window.onload = init = () => {
	// 버튼 이벤트 등록
	document.querySelector("#kakao").addEventListener("click", onKakao);

}


// 카카오 OAuth
const onKakao = async () => {

	let url = await fetch("/oauth/url", {
		headers: { "Content-Type": "application/json" },
		method: "GET"
	})
	.then(res => res.json())
	.then(res => res['kakao_oauth_url']);

	console.log(url);
	window.location.replace(url);

}


init();