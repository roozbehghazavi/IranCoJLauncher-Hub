EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 12)
	}

	StartVelocity()
	{
		keyf(0, 420)
	}

	StartVelocityRand()
	{
		keyv(0, 220, 260, 220)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodSplatter_trace.fx")
		Probability(0.7)
	}
}
