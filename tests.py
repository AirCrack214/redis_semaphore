from __future__ import absolute_import
import pytest
from distributed_semaphore import DistributedSemaphore


@pytest.mark.asyncio
async def test_successful_redis_connection():
    DistributedSemaphore(bounded_limit=1)

@pytest.mark.asyncio
async def test_lock():
    bounded_limit = 2
    s1 = DistributedSemaphore(bounded_limit=bounded_limit)
    s1.reset()
    s2 = DistributedSemaphore(bounded_limit=bounded_limit)
    s2.reset()

    assert s1.available_bounded_limit == bounded_limit
    assert s1.acquire() is not None
    assert s1.available_bounded_limit == (bounded_limit - 1)
    s1.release()
    assert s1.available_bounded_limit == bounded_limit

    assert s2.available_bounded_limit == bounded_limit
    assert s1.acquire() is not None
    assert s2.available_bounded_limit == (bounded_limit - 1)
    s1.release()

@pytest.mark.asyncio
async def test_with():
    bounded_limit = 2
    s1 = DistributedSemaphore(bounded_limit=bounded_limit)
    s1.reset()
    s2 = DistributedSemaphore(bounded_limit=bounded_limit)
    s2.reset()
    assert s1.available_bounded_limit == bounded_limit
    with s1 as sem:
        assert sem.available_bounded_limit == (bounded_limit - 1)
        with sem:
            assert sem.available_bounded_limit == (bounded_limit - 2)
    assert s1.available_bounded_limit == bounded_limit

@pytest.mark.asyncio
async def test_create_with_existing():
    bounded_limit = 2
    s1 = DistributedSemaphore(bounded_limit=bounded_limit)
    s1.reset()
    s2 = DistributedSemaphore(bounded_limit=bounded_limit)
    s2.reset()
    s3 = DistributedSemaphore(bounded_limit=bounded_limit)
    s3.reset()
    with s1 as s1:
        with s2 as s2:
            assert s1.available_bounded_limit == 0
            assert s2.available_bounded_limit == 0
            s3 = DistributedSemaphore(bounded_limit=bounded_limit * 10)
            assert s3.available_bounded_limit == 0

@pytest.mark.asyncio
async def test_acquire_without_connection():
    semaphore = DistributedSemaphore(bounded_limit=1)
    with pytest.raises(Exception):
        await semaphore.acquire()