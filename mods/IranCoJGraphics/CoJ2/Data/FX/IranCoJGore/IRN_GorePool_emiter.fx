EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 2.5)
	}

	GenType("continous")

	ParticleRate()
	{
		keyf(0, 30)
		keyf(0.7, 24)
		keyf(1.3, 14)
		keyf(1.5, 0)
	}

	StartVelocity()
	{
		keyf(0, 30)
	}

	StartVelocityRand()
	{
		keyv(0, 15, 0, 15)
		keyv(0.6, 45, 0, 45)
		keyv(1.4, 85, 0, 85)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodPool_trace.fx")
		Probability(1)
	}
}
