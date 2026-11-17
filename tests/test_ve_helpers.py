"""Unit cho scripts/ve.py - phần không cần browser.

mau/nen là cổng chặn token màu, rong_chu/cao_chu là phép đo đẻ ra mọi quyết
địch bố cục ("chữ quá nhỏ", hộp vừa chữ), còn dung() là lớp biên dịch spec
nơi mọi thông báo lỗi người đọc thấy khởi phát (Loi = ✗).
"""
import pytest

import theme as T
import ve


# ── ước lượng bề rộng/cao chữ ─────────────────────────────────────
class TestDoChu:
    def test_rong_mot_dong(self):
        assert ve.rong_chu('abc', 20) == 3 * 20 * 0.52

    def test_rong_lay_dong_dai_nhat(self):
        assert ve.rong_chu('ab\ncdef', 20) == 4 * 20 * 0.52

    def test_rong_chuoi_rong(self):
        assert ve.rong_chu('', 20) == 0

    def test_rong_nhan_duoc_so(self):
        # spec cho phep so; str() phai chay truoc khi do
        assert ve.rong_chu(5, 20) == 1 * 20 * 0.52

    def test_cao_mot_dong(self):
        assert ve.cao_chu('a', 20) == 1 * 20 * 1.25

    def test_cao_ba_dong(self):
        assert ve.cao_chu('a\nb\nc', 20) == 3 * 20 * 1.25


# ── cổng token màu ────────────────────────────────────────────────
class TestMauNen:
    def test_mau_token_thuong(self):
        assert ve.mau('ink') == T.LIGHT['ink']

    def test_mau_lit(self):
        assert ve.mau('lit-dark') == '#24272D'

    def test_mau_code_fg_dung_canh(self):
        assert ve.mau('code-fg') == ve.CANH_CHU

    def test_nen_rong_la_trong_suot(self):
        assert ve.nen(None) == 'transparent'
        assert ve.nen('') == 'transparent'

    def test_nen_soft(self):
        assert ve.nen('soft') == T.LIGHT['fill-soft']

    def test_nen_tint_theo_ten(self):
        assert ve.nen('l4') == T.FILL_LIGHT['fill-l4']

    def test_nen_code_dung_canh(self):
        assert ve.nen('code') == ve.CANH_NEN

    def test_nen_ink_lay_mau_dac(self):
        assert ve.nen('ink') == T.LIGHT['ink']

    def test_nen_lit(self):
        assert ve.nen('lit-light') == '#F4EFE4'

    def test_mau_sai_bao_loi_ten_token(self):
        with pytest.raises(ve.Loi) as e:
            ve.mau('khongtonai')
        msg = str(e.value)
        assert msg.startswith('✗ ')
        assert "color 'khongtonai' is not a token" in msg
        # danh sách gợi ý phải có cả token thường LẪN lit, kẻo người dùng
        # không biết đường dùng lit-dark/lit-light
        assert 'ink' in msg and 'lit-dark' in msg

    def test_nen_sai_bao_loi_ten_fill(self):
        with pytest.raises(ve.Loi) as e:
            ve.nen('zz')
        msg = str(e.value)
        assert "fill 'zz' does not exist" in msg
        assert 'soft' in msg and 'l4' in msg and 'lit-dark' in msg


# ── dung(): biên dịch spec, mọi đường lỗi đều phải thành Loi rõ nghĩa ──
HOP = [
    {'t': 'box', 'id': 'a', 'x': 0, 'y': 0, 'w': 60, 'h': 24, 'text': 'A'},
    {'t': 'box', 'id': 'b', 'x': 120, 'y': 0, 'w': 60, 'h': 24, 'text': 'B'},
    {'t': 'arrow', 'from': 'a', 'to': 'b', 'text': 'goi'},
]


class TestDung:
    def test_happy_path_tra_du_5_phan(self):
        sk, raw, hinh, lint_arrows, els = ve.dung(HOP)
        assert hinh['a']['t'] == 'box'
        assert raw == []
        assert len(sk) >= 2      # hai hop + nhan mui ten
        assert els == HOP or len(els) == len(HOP)

    def test_id_trung(self):
        spec = [dict(HOP[0]), dict(HOP[0])]
        with pytest.raises(ve.Loi, match="duplicate id 'a'"):
            ve.dung(spec)

    def test_mui_ten_chi_vao_id_khong_co(self):
        spec = [HOP[0], {'t': 'arrow', 'from': 'a', 'to': 'khongco'}]
        with pytest.raises(ve.Loi, match="matches no id"):
            ve.dung(spec)

    def test_mui_ten_chi_vao_text_tu_do(self):
        # bug that tu run dbi4: text tu do khong phai muc neo
        spec = [
            {'t': 'text', 'id': 'nhan', 'x': 0, 'y': 0, 'text': 'ghi chu'},
            {'t': 'box', 'id': 'a', 'x': 80, 'y': 0, 'w': 40, 'h': 20},
            {'t': 'arrow', 'from': 'a', 'to': 'nhan'},
        ]
        with pytest.raises(ve.Loi, match='is a free `text`'):
            ve.dung(spec)

    def test_mau_khong_hop_le_boc_lo_tu_dung(self):
        spec = [dict(HOP[0], color='hong')]
        with pytest.raises(ve.Loi, match="color 'hong' is not a token"):
            ve.dung(spec)

    def test_fill_khong_hop_le(self):
        spec = [dict(HOP[0], fill='tim')]
        with pytest.raises(ve.Loi, match="fill 'tim' does not exist"):
            ve.dung(spec)

    def test_chu_warn_tren_hinh_bi_hạ_ve_ink(self):
        # --warn tren --card chi 2.44:1 o theme sang - nhan chu phai ve ink
        spec = [dict(HOP[0], color='warn', text='canh bao')]
        sk, *_ = ve.dung(spec)
        lab = next(o['label'] for o in sk if o.get('type') == 'rectangle' and o.get('label'))
        assert lab['strokeColor'] == T.LIGHT['ink']
        # net ve van la warn
        o = next(o for o in sk if o.get('type') == 'rectangle')
        assert o['strokeColor'] == T.LIGHT['warn']
