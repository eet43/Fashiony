window.onload = init = () => {
	// 버튼 이벤트 등록
	document.querySelector("#logout").addEventListener("click", logout);

}


// 로그아웃 버튼 누르면 호출
const logout = async () => {
	window.location.replace('http://localhost:5000/oauth/logout');
}

init();