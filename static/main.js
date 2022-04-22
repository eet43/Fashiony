window.onload = init = () => {
	// 버튼 이벤트 등록
	document.querySelector("#kakao").addEventListener("click", onKakao);

}


// 카카오 서버로 url 요청
//올바른 url이 오기 전, 이동시키면 안되기 때문에 비동기 처리로 진행했다.
const onKakao = async () => {

	let url = await fetch("/oauth/url", {
		headers: { "Content-Type": "application/json" },
		method: "GET"
	})
	.then(res => res.json())
		//응답 값으로 카카오 서버로 요청할 수 있는 url이 온다
	.then(res => res['kakao_oauth_url']);
	//그 url로 이동시킨다
	window.location.replace(url);
}

init();