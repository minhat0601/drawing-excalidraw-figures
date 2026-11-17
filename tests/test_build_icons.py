"""Unit cho scripts/build_icons.py: dựng icon từ thư viện .excalidrawlib.

Chạy build() trên một cây thư viện giả trong tmp (đủ 12 nguồn của NGUON),
nên không đụng tới assets/icons.json thật. Hai bug của batch gần nhất đều
nằm ở đây: lọc tên với nguồn kiểu dict, và 'Cloud Function' ≠ 'Cloud Functions'.
"""
import json

import pytest

import build_icons as B


def rect(**kw):
    e = {'type': 'rectangle', 'x': 1, 'y': 2, 'width': 30, 'height': 30}
    e.update(kw)
    return e


def item(ten, els=None):
    return {'name': ten, 'elements': els if els is not None else [rect()]}


# Nguồn không lọc dùng chung tiền tố rỗng (it-icons, stick-people) nên tên
# phải khác nhau, không thì hai icon cùng khoá 'doi-tuong' ghi đè nhau.
TEN_KHONG_LOC = {'mateuszbaransanok': 'Doi Tuong', 'dwelle': 'Doi Tuong', 'dhtoran': 'Con Nguoi',
                 'finfin': 'Doi Tuong', 'anna-pastushko': 'Doi Tuong'}


@pytest.fixture
def cay(tmp_path):
    """Cây thư viện giả đủ 12 nguồn NGUON.

    Nguồn lọc theo tuple chứa đúng các tên được chọn cộng một icon mồi
    'Khong Chon' phải bị bỏ. Nguồn không lọc có một icon có tên (giữ) và
    một icon không tên (bỏ). Nguồn cũ (dict chỉ số) là mảng phần tử không tên.
    """
    goc = tmp_path / 'libraries'
    for rel, pre, *chon in B.NGUON:
        f = goc / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        if chon and isinstance(chon[0], dict):
            n = max(chon[0]) + 3                     # vài chỉ số ngoài danh sách làm mồi
            d = {'library': [[rect()] for _ in range(n)]}
        elif chon:
            # mồi phải bị bỏ; đặt tên khác nhau từng nguồn vì hai cặp nguồn
            # dùng chung tiền tố (azure-, db-) mà cùng khoá thì ghi đè nhau
            d = {'libraryItems': [item(t) for t in chon[0]] + [item(f'Khong Chon {pre}')]}
        else:
            d = {'libraryItems': [item(TEN_KHONG_LOC[rel.split('/')[0]]),
                                  {'name': '', 'elements': [rect()]}]}
        f.write_text(json.dumps(d), encoding='utf-8')
    return goc


def test_rutgon_bo_prefix_azure_chi_khi_la_azure():
    assert B.rutgon('azure-', 'Azure Cosmos DB') == 'Cosmos DB'
    assert B.rutgon('azure-', 'Virtual Machine') == 'Virtual Machine'
    assert B.rutgon('gcp-', 'Azure Gi Do') == 'Azure Gi Do'   # chỉ bỏ với tiền tố azure-


def test_rutgon_ten_ngan_thang_hon_ten_goc():
    assert B.rutgon('gcp-', 'Cloud Function') == 'Cloud Functions'
    assert B.rutgon('db-', 'Postgres Database') == 'postgres'


def test_build_giu_dung_ten_loc(cay, tmp_path):
    out = B.build(cay, tmp_path / 'icons.json')
    # nguồn lọc theo tuple: giữ đúng tên trong danh sách
    assert 'aws-ec2' in out and 'gcp-gke' in out
    # azure-: bỏ tiền tố 'Azure ' thừa
    assert 'azure-virtual-machine' in out
    assert 'azure-cosmos-db' in out
    # TEN_NGAN đổi tên khi thư viện đặt khác vẫn ra khoá quen thuộc
    assert 'gcp-cloud-functions' in out and 'db-postgres' in out and 'db-kafka' in out
    # nguồn cũ: đặt tên theo chỉ số
    assert 'tech-kubernetes' in out and 'tech-redis' in out
    # nguồn không lọc: icon không tên bị bỏ, icon có tên giữ nguyên khoá
    assert 'doi-tuong' in out and 'net-doi-tuong' in out


def test_build_bo_icon_ngoai_danh_sach_loc(cay, tmp_path):
    out = B.build(cay, tmp_path / 'icons.json')
    assert not any('khong-chon' in k for k in out)


def test_build_du_so_luong_icon(cay, tmp_path):
    dst = tmp_path / 'icons.json'
    out = B.build(cay, dst)
    du_kien = sum(1 for c in B.NGUON if len(c) == 2)                          # 5 nguồn không lọc
    du_kien += sum(len(c[2]) for c in B.NGUON if len(c) > 2 and not isinstance(c[2], dict))
    du_kien += len(B.TECH_LOGOS)                                              # nguồn kiểu dict
    assert len(out) == du_kien
    # ghi ra đúng đích truyền vào, không đụng assets/ thật
    assert json.loads(dst.read_text()).keys() == out.keys()


def test_build_loc_phan_tu_khong_ve_duoc(cay, tmp_path):
    # gắn vào EC2: 1 hình chữ nhật tốt + hit-area ẩn + phần tử đã xoá + text
    f = cay / 'childishgirl/aws-architecture-icons.excalidrawlib'
    d = json.loads(f.read_text())
    thu = next(it for it in d['libraryItems'] if it['name'] == 'EC2')
    thu['elements'] = [
        rect(),
        rect(opacity=0),                          # hit-area tàng hình -> bỏ
        rect(isDeleted=True),                     # đã xoá -> bỏ
        {'type': 'text', 'x': 0, 'y': 0},         # không phải hình -> bỏ
    ]
    f.write_text(json.dumps(d), encoding='utf-8')
    out = B.build(cay, tmp_path / 'icons.json')
    assert len(out['aws-ec2']['elements']) == 1


def test_build_lam_tron_toa_do(cay, tmp_path):
    f = cay / 'childishgirl/aws-architecture-icons.excalidrawlib'
    d = json.loads(f.read_text())
    next(it for it in d['libraryItems'] if it['name'] == 'EC2')['elements'] = [
        rect(x=1.236, y=2, width=30.111, height=30),
        {'type': 'line', 'x': 0, 'y': 0, 'points': [[1.236, 2], [3.456, 4]]},
    ]
    f.write_text(json.dumps(d), encoding='utf-8')
    els = B.build(cay, tmp_path / 'icons.json')['aws-ec2']['elements']
    assert els[0]['x'] == 1.24 and els[0]['width'] == 30.11
    assert els[1]['points'] == [[1.24, 2], [3.46, 4]]


def test_build_chuyen_strokesharpness_cu(cay, tmp_path):
    # thư viện cũ đánh dấu bo góc bằng strokeSharpness; bản mới cần roundness
    f = cay / 'childishgirl/aws-architecture-icons.excalidrawlib'
    d = json.loads(f.read_text())
    next(it for it in d['libraryItems'] if it['name'] == 'EC2')['elements'] = [rect(strokeSharpness='round')]
    f.write_text(json.dumps(d), encoding='utf-8')
    out = B.build(cay, tmp_path / 'icons.json')
    assert out['aws-ec2']['elements'][0]['roundness'] == {'type': 3}


def test_thieu_ten_thi_chet_ro_ten(cay, tmp_path):
    f = cay / 'chuqbach/data-platform.excalidrawlib'
    f.write_text(json.dumps({'libraryItems': [item('Elasticsearch')]}), encoding='utf-8')  # thiếu Kafka
    dst = tmp_path / 'icons.json'
    with pytest.raises(SystemExit, match='names not found'):
        B.build(cay, dst)
    assert not dst.exists()      # chết trước khi ghi


def test_chi_giu_truong_hinh_hoc_va_gan_src(cay, tmp_path):
    out = B.build(cay, tmp_path / 'icons.json')
    for e in out['aws-ec2']['elements']:
        assert set(e) <= set(B.GIU)
    assert out['aws-ec2']['src'] == 'childishgirl'
    assert out['tech-kubernetes']['src'] == 'maeddes'
