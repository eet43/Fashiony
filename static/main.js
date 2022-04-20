window.onload = init = () => {
	// 버튼 이벤트 등록
	document.querySelector("#kakao").addEventListener("click", onKakao);

	// 해당 함수는 Router 대신 실행하는 함수입니다.
}


// 카카오 OAuth
const onKakao = async () => {

	let url = await fetch("/oauth/url", {
		headers: { "Content-Type": "application/json" },
		method: "GET"
	})
	.then(res => res.json())
	.then(res => res['kakao_oauth_url']);

	window.location.replace(url);
	console.log(url);


}

// OAuth 로그인 후, 리다이렉트 페이지
const redirectPage = () => {
	// 만약 /oauth 으로 이동된다면 자동으로 해당 창은 닫습니다.
	const pathname = window.location.pathname;
	console.log(pathname);
	if (pathname.startsWith('/oauth')) {
		window.close();
	}
}

init();