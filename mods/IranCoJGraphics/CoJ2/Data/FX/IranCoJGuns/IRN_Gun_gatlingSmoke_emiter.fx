EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 0.8)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 2)
	}

	StartVelocity()
	{
		keyf(0, 600)
	}

	StartVelocityRand()
	{
		keyv(0, 90, 180, 180)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
